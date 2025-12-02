"""LLM-based maze solver that decides moves and tool usage."""

from typing import Any, Dict, List, Optional, Tuple
import os
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class LLMMazeSolver:
    """LLM-based maze solver that makes navigation decisions."""

    def __init__(self, model: str = "mistral", use_openai: bool = False):
        """
        Initialize LLM maze solver.

        Args:
            model: Model name (e.g., 'mistral', 'gpt-3.5-turbo', 'gpt-4')
            use_openai: If True, use OpenAI API instead of Ollama
        """
        self.model = model
        self.client = None
        self.use_openai = use_openai
        self.use_ollama = not use_openai

        if use_openai:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning(
                        "OPENAI_API_KEY not set. Set environment variable or use Ollama",
                        fallback="Using random decisions",
                    )
                    self.use_openai = False
                    self.use_ollama = False
                else:
                    self.client = OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized for maze solver", model=model)
            except ImportError:
                logger.warning(
                    "OpenAI not installed. Install with: pip install openai",
                    fallback="Using Ollama or random decisions",
                )
                self.use_openai = False
        else:
            try:
                import ollama
                self.client = ollama
                logger.info("Ollama client initialized for maze solver", model=model)
            except ImportError:
                logger.warning(
                    "Ollama not installed. Install with: pip install ollama",
                    fallback="Using random decisions",
                )
                self.use_ollama = False
            except Exception as e:
                logger.warning(
                    "Ollama client initialization failed",
                    error=str(e),
                    fallback="Using random decisions",
                )
                self.use_ollama = False

    def decide_action(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze: np.ndarray,
        recent_moves: List[Tuple[int, int]],
        tool_history: List[dict],
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Use LLM to decide next move.

        Args:
            agent_pos: Current agent position (row, col)
            goal_pos: Goal position (row, col)
            maze: Maze grid (0 = walkable, 1 = wall)
            recent_moves: Recent positions (last 5 moves)
            tool_history: History of tool queries

        Returns:
            Tuple of (action_index, reasoning_dict)
            action_index: 0=up, 1=down, 2=left, 3=right
        """
        if (not self.use_ollama and not self.use_openai) or self.client is None:
            # Fallback: greedy move
            return self._greedy_move(agent_pos, goal_pos, maze)

        try:
            # Get valid moves
            valid_moves = self._get_valid_moves(agent_pos, maze)

            # Build prompt for LLM
            prompt = self._build_decision_prompt(
                agent_pos, goal_pos, maze, valid_moves, recent_moves, tool_history
            )

            if self.use_openai:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=100,
                )
                decision_text = response.choices[0].message.content.strip().lower()
            else:
                # Use Ollama
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False,
                    options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
                )
                decision_text = response["response"].strip().lower()

            # Parse response to get action
            action = self._parse_action_decision(decision_text, valid_moves)

            return action, {
                "method": "llm",
                "reasoning": decision_text[:100],
                "model": self.model,
                "valid_moves": valid_moves,
            }

        except Exception as e:
            logger.warning(
                "LLM decision failed, using fallback",
                error=str(e),
            )
            return self._greedy_move(agent_pos, goal_pos, maze)

    def decide_tool_usage(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze_size: int,
        recent_success_rate: float,
        tool_history: List[dict],
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Use LLM to decide whether to query tool.

        Args:
            agent_pos: Current agent position
            goal_pos: Goal position
            maze_size: Size of the maze
            recent_success_rate: Recent tool success rate (0.0-1.0)
            tool_history: History of tool queries

        Returns:
            Tuple of (should_use_tool, reasoning_dict)
        """
        if (not self.use_ollama and not self.use_openai) or self.client is None:
            # Fallback: use tool if it's reliable
            return recent_success_rate > 0.5, {
                "method": "fallback",
                "reasoning": f"Tool success rate: {recent_success_rate:.0%}",
            }

        try:
            # Calculate distance
            distance = int(
                abs(agent_pos[0] - goal_pos[0]) + abs(agent_pos[1] - goal_pos[1])
            )

            # Build prompt for tool usage decision
            prompt = self._build_tool_decision_prompt(
                agent_pos, goal_pos, maze_size, distance, recent_success_rate
            )

            if self.use_openai:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=50,
                )
                decision_text = response.choices[0].message.content.strip().lower()
            else:
                # Use Ollama
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False,
                    options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
                )
                decision_text = response["response"].strip().lower()

            # Parse response
            should_use = "yes" in decision_text

            return should_use, {
                "method": "llm",
                "reasoning": decision_text[:100],
                "model": self.model,
            }

        except Exception as e:
            logger.warning(
                "LLM tool decision failed, using fallback",
                error=str(e),
            )
            return recent_success_rate > 0.5, {
                "method": "fallback",
                "reasoning": f"Tool success rate: {recent_success_rate:.0%}",
            }

    def _get_valid_moves(
        self, agent_pos: Tuple[int, int], maze: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Get list of valid moves from current position."""
        action_names = ["up", "down", "left", "right"]
        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        valid = []
        for idx, (dr, dc) in enumerate(action_deltas):
            new_r = agent_pos[0] + dr
            new_c = agent_pos[1] + dc

            if (
                0 <= new_r < maze.shape[0]
                and 0 <= new_c < maze.shape[1]
                and maze[new_r, new_c] == 0
            ):
                distance = abs(new_r - agent_pos[0]) + abs(new_c - agent_pos[1])
                valid.append({
                    "direction": action_names[idx],
                    "action": idx,
                    "position": (new_r, new_c),
                })

        return valid

    def _build_decision_prompt(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze: np.ndarray,
        valid_moves: List[Dict[str, Any]],
        recent_moves: List[Tuple[int, int]],
        tool_history: List[dict],
    ) -> str:
        """Build prompt for LLM to decide next move."""
        # Calculate distance
        distance = int(
            abs(agent_pos[0] - goal_pos[0]) + abs(agent_pos[1] - goal_pos[1])
        )

        # Count recent tool usage
        recent_tools = len([t for t in tool_history[-5:] if t])

        # Format valid moves
        moves_str = "\n".join(
            [f"  - {m['direction']}: position {m['position']}" for m in valid_moves]
        )

        prompt = f"""You are a maze navigation agent. Decide your next move.

Current Situation:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Distance to goal: {distance} steps
- Maze size: {maze.shape[0]}x{maze.shape[1]}
- Recent tool queries (last 5): {recent_tools}

Valid Moves:
{moves_str}

Decide which direction to move. Consider:
1. Move closer to goal when possible
2. Avoid revisiting recent positions
3. Choose the move that minimizes distance to goal

Respond with ONLY the direction: up, down, left, or right

Decision: """
        return prompt

    def _build_tool_decision_prompt(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze_size: int,
        distance: int,
        success_rate: float,
    ) -> str:
        """Build prompt for LLM to decide tool usage."""
        return f"""You are a maze navigation agent. Decide if you should use a pathfinding tool.

Current Situation:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Maze size: {maze_size}x{maze_size}
- Distance to goal: {distance} steps
- Tool reliability (success rate): {success_rate:.0%}

Use the tool if:
1. You're far from goal (distance > {maze_size//2})
2. You're confused or stuck
3. You've made many recent moves without progress

Answer with only YES or NO.

Decision: """

    def _parse_action_decision(
        self, response: str, valid_moves: List[Dict[str, Any]]
    ) -> int:
        """Parse LLM response to action index."""
        response_lower = response.lower().strip()

        # Try to find direction in response
        for move in valid_moves:
            if move["direction"] in response_lower:
                return move["action"]

        # Fallback: return first valid move
        if valid_moves:
            return valid_moves[0]["action"]

        # Last resort: stay (shouldn't happen)
        return 0

    def _greedy_move(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze: np.ndarray,
    ) -> Tuple[int, Dict[str, Any]]:
        """Fallback: greedy move towards goal."""
        valid_moves = self._get_valid_moves(agent_pos, maze)

        if not valid_moves:
            return 0, {
                "method": "greedy",
                "reasoning": "No valid moves",
            }

        # Choose move closest to goal
        best_move = min(
            valid_moves,
            key=lambda m: abs(m["position"][0] - goal_pos[0])
            + abs(m["position"][1] - goal_pos[1]),
        )

        return best_move["action"], {
            "method": "greedy",
            "reasoning": f"Moving {best_move['direction']} towards goal",
        }

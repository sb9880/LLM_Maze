"""LLM-based maze solver that decides moves and tool usage."""

from typing import Any, Dict, List, Optional, Tuple
import os
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class LLMMazeSolver:
    """LLM-based maze solver that makes navigation decisions."""

    def __init__(self, model: str = "mistral", use_openai: bool = False, max_history_messages: int = 20):
        """
        Initialize LLM maze solver.

        Args:
            model: Model name (e.g., 'mistral', 'gpt-3.5-turbo', 'gpt-4')
            use_openai: If True, use OpenAI API instead of Ollama
            max_history_messages: Maximum number of conversation messages to keep (default 20)
        """
        self.model = model
        self.client = None
        self.use_openai = use_openai
        self.use_ollama = not use_openai
        self.max_history_messages = max_history_messages

        # Conversation history for persistent memory across steps
        self.conversation_history = []
        self.episode_initialized = False

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

    def reset_episode(self, goal_pos: Optional[Tuple[int, int]] = None, maze_size: Optional[int] = None):
        """
        Reset conversation history for new episode.

        Args:
            goal_pos: Goal position for this episode
            maze_size: Size of the maze
        """
        self.conversation_history = []
        self.episode_initialized = False

        # Add system prompt at start of episode
        if goal_pos and maze_size:
            system_prompt = f"""You are an intelligent maze navigation agent. Your task is to reach the goal position {goal_pos} in a {maze_size}x{maze_size} maze.

Key Rules:
1. Remember your previous positions to avoid loops
2. Consider whether to use the pathfinding tool - it may be unreliable
3. Make strategic decisions based on your progress
4. Each step, decide: (a) Use tool? (b) Which direction to move?

I will give you updates at each step. Make smart decisions to reach the goal efficiently."""

            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
            self.episode_initialized = True

        logger.info("Episode reset for LLM solver", model=self.model)

    def _trim_conversation_history(self):
        """Keep only recent conversation history to avoid token limits."""
        if len(self.conversation_history) > self.max_history_messages:
            # Always keep the system message (first message)
            system_message = self.conversation_history[0] if self.conversation_history else None

            # Keep only the most recent messages
            recent_messages = self.conversation_history[-(self.max_history_messages - 1):]

            # Rebuild history with system message + recent messages
            if system_message:
                self.conversation_history = [system_message] + recent_messages
            else:
                self.conversation_history = recent_messages

    def decide_step(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze: np.ndarray,
        recent_moves: List[Tuple[int, int]],
        tool_history: List[dict],
        allow_tool: bool = True,
        recent_success_rate: float = 0.5,
    ) -> Tuple[bool, Optional[int], Dict[str, Any]]:
        """
        Single LLM call to decide both tool usage AND next action.

        Args:
            agent_pos: Current position
            goal_pos: Goal position
            maze: Maze grid
            recent_moves: Recent positions
            tool_history: Tool query history
            allow_tool: Whether tool usage is allowed
            recent_success_rate: Tool reliability (0.0-1.0)

        Returns:
            Tuple of (should_use_tool, action_index, reasoning_dict)
        """
        if (not self.use_ollama and not self.use_openai) or self.client is None:
            # Fallback: greedy move without tool
            action, _ = self._greedy_move(agent_pos, goal_pos, maze)
            return False, action, {"method": "fallback"}

        try:
            # Get valid moves
            valid_moves = self._get_valid_moves(agent_pos, maze)

            # Build combined prompt
            prompt = self._build_combined_prompt(
                agent_pos, goal_pos, maze, valid_moves, recent_moves,
                tool_history, allow_tool, recent_success_rate
            )

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            # Trim history to prevent token limit issues
            self._trim_conversation_history()

            if self.use_openai:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.3,
                    max_tokens=150,
                )
                decision_text = response.choices[0].message.content.strip().lower()

                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })
            else:
                # Ollama
                full_prompt = self._format_ollama_prompt(self.conversation_history)
                response = self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    stream=False,
                    options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
                )
                decision_text = response["response"].strip().lower()

                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })

            # Parse response for both tool decision and action
            # More flexible parsing - check for various ways LLM might say "yes" to tool
            should_use_tool = (
                "tool: yes" in decision_text or
                "use tool: yes" in decision_text or
                "tool:yes" in decision_text or
                "use the tool" in decision_text or
                "using tool" in decision_text or
                "will use tool" in decision_text or
                "query tool" in decision_text or
                "ask tool" in decision_text
            ) and not (
                "tool: no" in decision_text or
                "use tool: no" in decision_text or
                "not use tool" in decision_text or
                "won't use tool" in decision_text or
                "without tool" in decision_text
            )

            action = self._parse_action_decision(decision_text, valid_moves)

            # Debug logging to see what LLM is saying
            logger.info(
                "llm_step_decision",
                response=decision_text[:200],  # First 200 chars
                tool_decision=should_use_tool,
                action=action,
            )

            # Print first few responses of episode to console for debugging
            if len(self.conversation_history) <= 10:  # First 5 steps (2 messages per step)
                print(f"[DEBUG Step {len(self.conversation_history)//2}] LLM: {decision_text[:200]}")
                print(f"        → Tool decision: {should_use_tool}, Action: {action}")

            return should_use_tool, action, {
                "method": "llm_combined",
                "llm_response": decision_text,
                "model": self.model,
                "tool_decision": should_use_tool,
            }

        except Exception as e:
            logger.warning(
                "LLM combined decision failed, using fallback",
                error=str(e),
            )
            action, _ = self._greedy_move(agent_pos, goal_pos, maze)
            return False, action, {
                "method": "fallback",
                "error": str(e),
            }

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

            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            # Trim history to prevent token limit issues
            self._trim_conversation_history()

            if self.use_openai:
                # Use OpenAI API with full conversation history
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.3,
                    max_tokens=100,
                )
                decision_text = response.choices[0].message.content.strip().lower()

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })
            else:
                # Use Ollama - need to format conversation as single prompt
                # Ollama doesn't support conversation history directly, so we'll include recent context
                full_prompt = self._format_ollama_prompt(self.conversation_history)
                response = self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    stream=False,
                    options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
                )
                decision_text = response["response"].strip().lower()

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })

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

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            # Trim history to prevent token limit issues
            self._trim_conversation_history()

            if self.use_openai:
                # Use OpenAI API with conversation history
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    temperature=0.3,
                    max_tokens=50,
                )
                decision_text = response.choices[0].message.content.strip().lower()

                # Add response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })
            else:
                # Use Ollama with formatted prompt
                full_prompt = self._format_ollama_prompt(self.conversation_history)
                response = self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    stream=False,
                    options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
                )
                decision_text = response["response"].strip().lower()

                # Add response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": decision_text
                })

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

    def _build_combined_prompt(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze: np.ndarray,
        valid_moves: List[Dict[str, Any]],
        recent_moves: List[Tuple[int, int]],
        tool_history: List[dict],
        allow_tool: bool,
        recent_success_rate: float,
    ) -> str:
        """Build prompt for COMBINED tool + action decision."""
        distance = int(abs(agent_pos[0] - goal_pos[0]) + abs(agent_pos[1] - goal_pos[1]))
        recent_tools = len([t for t in tool_history[-5:] if t])

        # Format valid moves
        moves_str = "\n".join(
            [f"  - {m['direction']}: goes to {m['position']}" for m in valid_moves]
        )

        # Format recent positions
        recent_str = ", ".join([str(p) for p in recent_moves[-3:]]) if recent_moves else "none"

        tool_info = ""
        if allow_tool:
            tool_info = f"""
Tool Information:
- A pathfinding tool is available (may have errors)
- Tool reliability: {recent_success_rate:.0%}
- Recent tool usage (last 5 steps): {recent_tools} times
"""

        prompt = f"""Current step decision:

Position: {agent_pos}
Goal: {goal_pos}
Distance to goal: {distance} steps
Recent positions: {recent_str}
{tool_info}
Valid moves:
{moves_str}

Make TWO decisions:
1. Should you use the pathfinding tool? (if allowed and seems helpful)
2. Which direction should you move?

Consider:
- Avoid loops (don't revisit recent positions)
- Tool may be unreliable - use when needed but don't blindly trust
- Move toward goal when possible

Response format:
Tool: yes/no
Direction: up/down/left/right
Reasoning: brief explanation"""

        return prompt

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

    def _format_ollama_prompt(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Format conversation history for Ollama (which doesn't support chat format natively).

        Args:
            conversation_history: List of conversation messages

        Returns:
            Formatted prompt string
        """
        if not conversation_history:
            return ""

        # Keep last 10 messages to avoid context overflow
        recent_history = conversation_history[-10:]

        formatted = []
        for msg in recent_history:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                formatted.append(f"SYSTEM: {content}\n")
            elif role == "user":
                formatted.append(f"USER: {content}\n")
            elif role == "assistant":
                formatted.append(f"ASSISTANT: {content}\n")

        formatted.append("ASSISTANT: ")
        return "\n".join(formatted)

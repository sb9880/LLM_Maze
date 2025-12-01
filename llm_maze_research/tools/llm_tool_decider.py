"""LLM-based tool usage decision maker using Ollama."""

from typing import Tuple, Optional, Dict, Any
import os
import structlog

logger = structlog.get_logger(__name__)


class LLMToolDecider:
    """LLM-based tool usage decision maker."""

    def __init__(self, model: str = "mistral", use_ollama: bool = True):
        """
        Initialize LLM tool decider.

        Args:
            model: Model name (e.g., 'mistral', 'neural-chat', 'phi')
            use_ollama: Whether to use Ollama (local) or skip LLM
        """
        self.model = model
        self.use_ollama = use_ollama
        self.client = None

        if use_ollama:
            try:
                import ollama

                self.client = ollama
                logger.info("Ollama client initialized", model=model)
            except ImportError:
                logger.warning(
                    "Ollama not installed. Install with: pip install ollama",
                    fallback="Using random decision",
                )
                self.use_ollama = False
            except Exception as e:
                logger.warning(
                    "Ollama client initialization failed",
                    error=str(e),
                    fallback="Using random decision",
                )
                self.use_ollama = False

    def decide(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze_size: int,
        recent_success_rate: float,
        tool_history: list,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Decide whether to use the tool based on LLM reasoning.

        Args:
            agent_pos: Current agent position (row, col)
            goal_pos: Goal position (row, col)
            maze_size: Size of the maze
            recent_success_rate: Recent tool success rate (0.0-1.0)
            tool_history: History of tool queries and outcomes

        Returns:
            Tuple of (should_use_tool: bool, reasoning_dict)
        """
        if not self.use_ollama or self.client is None:
            # Fallback: use random (default behavior)
            return self._fallback_decision(recent_success_rate)

        try:
            # Calculate distance to goal
            distance = abs(agent_pos[0] - goal_pos[0]) + abs(
                agent_pos[1] - goal_pos[1]
            )

            # Build prompt for LLM
            prompt = self._build_prompt(
                agent_pos, goal_pos, maze_size, distance, recent_success_rate
            )

            # Get LLM decision
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.3, "top_k": 2, "top_p": 0.5},
            )

            # Parse response
            decision_text = response["response"].strip().lower()
            should_use = self._parse_decision(decision_text)

            return should_use, {
                "method": "llm",
                "reasoning": decision_text[:100],
                "model": self.model,
            }

        except Exception as e:
            logger.warning(
                "LLM decision failed, using fallback",
                error=str(e),
            )
            return self._fallback_decision(recent_success_rate)

    def _build_prompt(
        self,
        agent_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        maze_size: int,
        distance: int,
        success_rate: float,
    ) -> str:
        """Build prompt for LLM decision."""
        return f"""You are a maze navigation agent. Decide if you should use a pathfinding tool.

Current situation:
- Agent position: {agent_pos}
- Goal position: {goal_pos}
- Maze size: {maze_size}x{maze_size}
- Distance to goal: {distance} steps
- Tool success rate (last 5 uses): {success_rate:.0%}

Answer with only YES or NO. Use the tool if:
1. You're far from goal (distance > {maze_size//2}) AND tool is reliable (success > 50%)
2. You're confused (many failed attempts)

Otherwise navigate independently.

Decision: """

    def _parse_decision(self, response: str) -> bool:
        """Parse LLM response to boolean decision."""
        if "yes" in response:
            return True
        if "no" in response:
            return False
        # Default to False if unclear
        return False

    def _fallback_decision(
        self, recent_success_rate: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fallback decision based on success rate."""
        # Use tool if it's been reliable (>50% success)
        should_use = recent_success_rate > 0.5

        return should_use, {
            "method": "fallback",
            "reasoning": f"Tool success rate: {recent_success_rate:.0%}",
            "model": "none",
        }

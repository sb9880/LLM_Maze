"""Base agent implementations for maze navigation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import structlog

from agents.prompts import format_system_prompt, SYSTEM_PROMPT_BASE
from agents.strategies import DecisionStrategy, AdaptiveStrategy
from agents.llm_maze_solver import LLMMazeSolver
from tools.astar_planner import AStarPlanner
from tools.llm_tool_decider import LLMToolDecider

logger = structlog.get_logger(__name__)


@dataclass
class AgentConfig:
    """Configuration for maze navigation agent."""

    model: str = "gpt-4-turbo"
    strategy: str = "adaptive"  # adaptive, tool_trusting, tool_avoiding
    temperature: float = 0.7
    max_steps: int = 500
    seed: int = 42
    use_tool: bool = True
    tool_query_frequency: float = 0.5  # How often to query tool
    use_llm_tool_decider: bool = False  # Use LLM to decide tool usage
    llm_model: str = "mistral"  # Ollama model for tool decision


class BaseAgent:
    """Base agent for maze navigation."""

    def __init__(
        self,
        config: AgentConfig,
        planner: Optional[AStarPlanner] = None,
        strategy: Optional[DecisionStrategy] = None,
    ):
        """
        Initialize base agent.

        Args:
            config: Agent configuration
            planner: A* planner tool
            strategy: Decision strategy
        """
        self.config = config
        self.planner = planner
        self.strategy = strategy or AdaptiveStrategy()
        self.rng = np.random.RandomState(config.seed)

        # Initialize LLM tool decider if enabled
        self.llm_tool_decider = None
        if config.use_llm_tool_decider:
            self.llm_tool_decider = LLMToolDecider(
                model=config.llm_model,
                use_ollama=True
            )

        # Tracking
        self.episode_trajectory = []
        self.tool_queries = []
        self.decisions = []

    def reset(self) -> None:
        """Reset agent state for new episode."""
        self.episode_trajectory = []
        self.tool_queries = []
        self.decisions = []

    def step(
        self,
        obs: dict,
        allow_tool: bool = True,
    ) -> int:
        """
        Execute one step in environment.

        Args:
            obs: Observation dict with agent_pos, goal_pos, maze
            allow_tool: Whether to allow tool usage

        Returns:
            Action index (0=up, 1=down, 2=left, 3=right)
        """
        agent_pos = obs["agent_pos"]
        goal_pos = obs["goal_pos"]
        maze = obs["maze"]

        # Record trajectory
        self.episode_trajectory.append({
            "step": len(self.episode_trajectory),
            "agent_pos": tuple(agent_pos),
            "goal_pos": tuple(goal_pos),
        })

        # Decide whether to query tool
        should_query_tool = False
        llm_decision_info = None

        if allow_tool and self.planner:
            if self.llm_tool_decider:
                # Use LLM to decide
                maze_size = maze.shape[0]
                recent_success_rate = self._get_recent_tool_success_rate()
                should_query_tool, llm_decision_info = self.llm_tool_decider.decide(
                    agent_pos=tuple(agent_pos),
                    goal_pos=tuple(goal_pos),
                    maze_size=maze_size,
                    recent_success_rate=recent_success_rate,
                    tool_history=self.tool_queries,
                )
            else:
                # Use random probability
                should_query_tool = self.rng.random() < self.config.tool_query_frequency

        # Query tool if decided
        planner_suggestion = None
        if should_query_tool:
            planner_suggestion = self.planner.plan(
                maze,
                tuple(agent_pos),
                tuple(goal_pos),
            )
            self.tool_queries.append({
                "step": len(self.episode_trajectory) - 1,
                "position": tuple(agent_pos),
                "suggestion": planner_suggestion,
                "llm_decision": llm_decision_info,
            })

        # Get decision from strategy
        action, decision_info = self.strategy.decide(
            agent_pos,
            goal_pos,
            maze,
            planner_suggestion,
            self.tool_queries,
        )

        # Record decision
        decision_info.update({
            "step": len(self.decisions),
            "action": action,
            "position": tuple(agent_pos),
            "goal": tuple(goal_pos),
        })
        self.decisions.append(decision_info)

        return action

    def _get_recent_tool_success_rate(self) -> float:
        """Calculate recent tool success rate from last 5 queries."""
        if not self.tool_queries:
            return 0.5  # Default: neutral trust

        recent = self.tool_queries[-5:]
        if not recent:
            return 0.5

        # Count helpful suggestions (those that moved toward goal)
        helpful_count = 0
        for query in recent:
            suggestion = query.get("suggestion")
            if suggestion and len(suggestion) > 1:
                helpful_count += 1

        return helpful_count / len(recent) if recent else 0.5

    def get_episode_stats(self) -> dict:
        """Get statistics for current episode."""
        if not self.episode_trajectory:
            return {}

        tool_usage_count = len(self.tool_queries)
        total_steps = len(self.episode_trajectory)

        return {
            "total_steps": total_steps,
            "tool_queries": tool_usage_count,
            "tool_usage_rate": (
                tool_usage_count / total_steps if total_steps > 0 else 0.0
            ),
            "trajectory": self.episode_trajectory,
            "decisions": self.decisions,
        }


class MazeAgent(BaseAgent):
    """LLM-based maze agent using LangChain."""

    def __init__(
        self,
        config: AgentConfig,
        planner: Optional[AStarPlanner] = None,
        strategy: Optional[DecisionStrategy] = None,
    ):
        """Initialize maze agent."""
        super().__init__(config, planner, strategy)

        # Try to initialize LLM if configured
        self.llm = None
        if config.model.startswith("gpt"):
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model_name=config.model,
                    temperature=config.temperature,
                )
            except Exception as e:
                logger.warning(f"LangChain OpenAI not available: {e}")
        elif config.model.startswith("claude"):
            try:
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    model=config.model,
                    temperature=config.temperature,
                )
            except Exception as e:
                logger.warning(f"LangChain Anthropic not available: {e}")

    def step(
        self,
        obs: dict,
        allow_tool: bool = True,
    ) -> int:
        """
        Execute one step with LLM reasoning (if available).

        Args:
            obs: Observation dict
            allow_tool: Whether to allow tool usage

        Returns:
            Action index
        """
        agent_pos = obs["agent_pos"]
        goal_pos = obs["goal_pos"]
        maze = obs["maze"]

        # Record trajectory
        self.episode_trajectory.append({
            "step": len(self.episode_trajectory),
            "agent_pos": tuple(agent_pos),
            "goal_pos": tuple(goal_pos),
        })

        # Calculate distance
        distance = int(
            np.abs(agent_pos[0] - goal_pos[0])
            + np.abs(agent_pos[1] - goal_pos[1])
        )

        # Query tool if appropriate
        planner_suggestion = None
        if (
            allow_tool
            and self.planner
            and self.rng.random() < self.config.tool_query_frequency
        ):
            planner_suggestion = self.planner.plan(
                maze,
                tuple(agent_pos),
                tuple(goal_pos),
            )
            self.tool_queries.append({
                "step": len(self.episode_trajectory) - 1,
                "position": tuple(agent_pos),
                "suggestion": planner_suggestion,
            })

        # Get decision from strategy
        action, decision_info = self.strategy.decide(
            agent_pos,
            goal_pos,
            maze,
            planner_suggestion,
            self.tool_queries,
        )

        # Record decision
        decision_info.update({
            "step": len(self.decisions),
            "action": action,
            "position": tuple(agent_pos),
            "goal": tuple(goal_pos),
        })
        self.decisions.append(decision_info)

        return action


class LLMSolverAgent(BaseAgent):
    """LLM-based maze solver that makes navigation and tool decisions."""

    def __init__(
        self,
        config: AgentConfig,
        planner: Optional[AStarPlanner] = None,
        strategy: Optional[DecisionStrategy] = None,
    ):
        """Initialize LLM solver agent."""
        super().__init__(config, planner, strategy)

        # Initialize LLM maze solver
        self.maze_solver = LLMMazeSolver(model=config.llm_model)

    def step(
        self,
        obs: dict,
        allow_tool: bool = True,
    ) -> int:
        """
        Execute one step using LLM for both action and tool decisions.

        Args:
            obs: Observation dict with agent_pos, goal_pos, maze
            allow_tool: Whether to allow tool usage

        Returns:
            Action index (0=up, 1=down, 2=left, 3=right)
        """
        agent_pos = obs["agent_pos"]
        goal_pos = obs["goal_pos"]
        maze = obs["maze"]

        # Record trajectory
        self.episode_trajectory.append({
            "step": len(self.episode_trajectory),
            "agent_pos": tuple(agent_pos),
            "goal_pos": tuple(goal_pos),
        })

        # Get recent moves (last 5)
        recent_moves = [t["agent_pos"] for t in self.episode_trajectory[-5:]]

        # Step 1: LLM decides whether to use tool
        planner_suggestion = None
        tool_reasoning = None
        if allow_tool and self.planner:
            maze_size = maze.shape[0]
            recent_success_rate = self._get_recent_tool_success_rate()
            should_query_tool, tool_reasoning = self.maze_solver.decide_tool_usage(
                agent_pos=tuple(agent_pos),
                goal_pos=tuple(goal_pos),
                maze_size=maze_size,
                recent_success_rate=recent_success_rate,
                tool_history=self.tool_queries,
            )

            # Query tool if LLM decided to
            if should_query_tool:
                planner_suggestion = self.planner.plan(
                    maze,
                    tuple(agent_pos),
                    tuple(goal_pos),
                )
                self.tool_queries.append({
                    "step": len(self.episode_trajectory) - 1,
                    "position": tuple(agent_pos),
                    "suggestion": planner_suggestion,
                    "llm_decision": tool_reasoning,
                })

        # Step 2: LLM decides next action
        action, action_reasoning = self.maze_solver.decide_action(
            agent_pos=tuple(agent_pos),
            goal_pos=tuple(goal_pos),
            maze=maze,
            recent_moves=recent_moves,
            tool_history=self.tool_queries,
        )

        # Record decision with combined reasoning
        decision_info = {
            "step": len(self.decisions),
            "action": action,
            "position": tuple(agent_pos),
            "goal": tuple(goal_pos),
            "strategy": "llm_solver",
            "action_reasoning": action_reasoning,
            "tool_reasoning": tool_reasoning,
            "used_tool": planner_suggestion is not None,
        }
        self.decisions.append(decision_info)

        return action

"""Experiment runner for maze navigation tasks."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

import structlog

from agents.base_agent import AgentConfig, BaseAgent, MazeAgent, LLMSolverAgent
from agents.strategies import (
    AdaptiveStrategy,
    ToolAvoidingStrategy,
    ToolTrustingStrategy,
)
from envs.grid_world import GridWorld, GridWorldConfig
from experiments.metrics import MetricsCollector
from tools.astar_planner import AStarPlanner
from tools.noise_models import NoiseFactory

logger = structlog.get_logger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration for an experiment run."""

    # Environment
    maze_size: int = 16
    maze_difficulty: str = "medium"
    num_episodes: int = 10

    # Agent
    model: str = "gpt-3.5-turbo"
    agent_strategy: str = "adaptive"
    temperature: float = 0.7
    use_openai: bool = False

    # Tool
    use_tool: bool = True
    noise_type: str = "random"
    noise_level: float = 0.3
    tool_query_frequency: float = 0.5

    # Execution
    seed: int = 42
    max_steps_per_episode: int = 500


class ExperimentRunner:
    """Run maze navigation experiments."""

    def __init__(self, config: ExperimentConfig):
        """
        Initialize experiment runner.

        Args:
            config: Experiment configuration
        """
        self.config = config
        self.experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        self.metrics_collector = MetricsCollector()

    def run(self) -> Dict[str, Any]:
        """
        Run complete experiment.

        Returns:
            Results dictionary
        """
        logger.info(
            "experiment_start",
            experiment_id=self.experiment_id,
            config=vars(self.config),
        )

        start_time = datetime.now()

        for episode_num in range(self.config.num_episodes):
            self._run_episode(episode_num)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Aggregate results
        aggregated_metrics = self.metrics_collector.aggregate_metrics()
        aggregated_metrics["duration_seconds"] = duration

        logger.info(
            "experiment_complete",
            experiment_id=self.experiment_id,
            metrics=aggregated_metrics,
        )

        return {
            "experiment_id": self.experiment_id,
            "config": vars(self.config),
            "metrics": aggregated_metrics,
            "episodes": self.metrics_collector.episodes,
        }

    def _run_episode(self, episode_num: int) -> None:
        """Run a single episode."""
        episode_id = f"{self.experiment_id}_ep{episode_num}"

        # Print progress to console
        print(f"\n{'='*80}")
        print(f"Starting Episode {episode_num}/{self.config.num_episodes}")
        print(f"{'='*80}")

        logger.info(
            "episode_start",
            episode_id=episode_id,
            episode_num=episode_num,
        )

        # Create environment
        env_config = GridWorldConfig(
            maze_size=self.config.maze_size,
            difficulty=self.config.maze_difficulty,
            seed=self.config.seed + episode_num,  # Vary seed
            max_steps=self.config.max_steps_per_episode,
        )
        env = GridWorld(env_config)

        # Create planner with noise
        noise_model = NoiseFactory.create(
            self.config.noise_type,
            self.config.noise_level,
        )
        planner = AStarPlanner(noise_model=noise_model)

        # Create agent with strategy
        agent_config = AgentConfig(
            model=self.config.model,
            strategy=self.config.agent_strategy,
            temperature=self.config.temperature,
            seed=self.config.seed + episode_num,
            use_tool=self.config.use_tool,
            tool_query_frequency=self.config.tool_query_frequency,
            use_openai=self.config.use_openai,
        )

        strategy = self._create_strategy(
            self.config.agent_strategy,
            self.config.seed + episode_num,
        )

        # Create appropriate agent type
        if self.config.agent_strategy == "llm_solver":
            # Use LLM solver agent
            agent = LLMSolverAgent(agent_config, planner=planner, strategy=strategy)
        else:
            # Try to use MazeAgent, fall back to BaseAgent if LLM unavailable
            try:
                agent = MazeAgent(agent_config, planner=planner, strategy=strategy)
            except Exception as e:
                logger.warning(
                    "MazeAgent initialization failed, falling back to BaseAgent",
                    error=str(e),
                )
                agent = BaseAgent(agent_config, planner=planner, strategy=strategy)

        # Run episode
        obs, info = env.reset()
        done = False
        success = False

        # Reset agent for new episode (with goal position and maze size for LLM context)
        goal_pos = tuple(obs["goal_pos"])
        maze_size = obs["maze"].shape[0]
        agent.reset(goal_pos=goal_pos, maze_size=maze_size)

        while not done:
            action = agent.step(obs, allow_tool=self.config.use_tool)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            if terminated:
                success = True

        # Get optimal path
        optimal_path = env.get_optimal_path()
        optimal_length = len(optimal_path) if optimal_path else float("inf")

        # Collect metrics
        self.metrics_collector.add_episode(
            episode_id=episode_id,
            trajectory=agent.episode_trajectory,
            decisions=agent.decisions,
            success=success,
            optimal_path_length=optimal_length,
            tool_queries=agent.tool_queries,
            maze=env.maze.tolist(),
        )

        # Print episode completion
        steps = len(agent.episode_trajectory)
        tool_queries = len(agent.tool_queries)
        print(f"Episode {episode_num} Complete: {'✓ SUCCESS' if success else '✗ FAILED'} | Steps: {steps} | Tool Queries: {tool_queries}")

        logger.info(
            "episode_complete",
            episode_id=episode_id,
            success=success,
            steps=steps,
        )

    def _create_strategy(self, strategy_name: str, seed: int) -> Any:
        """Create decision strategy."""
        if strategy_name == "tool_trusting":
            return ToolTrustingStrategy()
        elif strategy_name == "tool_avoiding":
            return ToolAvoidingStrategy()
        elif strategy_name == "adaptive":
            return AdaptiveStrategy(initial_trust=0.5)
        elif strategy_name == "llm_solver":
            # LLMSolverAgent doesn't use strategies, but we still need to return one
            # Return adaptive as default (won't be used)
            return AdaptiveStrategy(initial_trust=0.5)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

    def get_results(self) -> Dict[str, Any]:
        """Get aggregated results."""
        return {
            "experiment_id": self.experiment_id,
            "config": vars(self.config),
            "metrics": self.metrics_collector.aggregate_metrics(),
            "episodes": self.metrics_collector.episodes,
        }

"""Structured logging for agent actions and experiments."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog


@dataclass
class AgentActionLog:
    """Log entry for a single agent action."""

    timestamp: str
    episode_id: str
    step: int
    action: str
    agent_pos: tuple
    goal_pos: tuple
    used_tool: bool
    tool_suggestion: Optional[List[tuple]]
    decision_reason: str
    distance_to_goal: int


@dataclass
class EpisodeLog:
    """Log entry for a complete episode."""

    episode_id: str
    timestamp: str
    model: str
    strategy: str
    maze_difficulty: str
    maze_size: int
    success: bool
    total_steps: int
    optimal_steps: int
    tool_query_count: int
    tool_usage_rate: float
    tool_accuracy_rate: float
    path_optimality: float
    duration_seconds: float


class ExperimentLogger:
    """Logger for experiment runs."""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize experiment logger.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir or "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger()

    def log_episode_start(
        self,
        episode_id: str,
        model: str,
        strategy: str,
        maze_config: dict,
    ) -> None:
        """Log start of episode."""
        self.logger.info(
            "episode_start",
            episode_id=episode_id,
            model=model,
            strategy=strategy,
            maze_config=maze_config,
        )

    def log_agent_action(
        self,
        episode_id: str,
        step: int,
        action: str,
        agent_pos: tuple,
        goal_pos: tuple,
        used_tool: bool,
        tool_suggestion: Optional[List[tuple]],
        decision_reason: str,
        distance_to_goal: int,
    ) -> None:
        """Log a single agent action."""
        self.logger.info(
            "agent_action",
            episode_id=episode_id,
            step=step,
            action=action,
            agent_pos=agent_pos,
            goal_pos=goal_pos,
            used_tool=used_tool,
            tool_suggestion=tool_suggestion,
            decision_reason=decision_reason,
            distance_to_goal=distance_to_goal,
        )

    def log_episode_complete(
        self,
        episode_log: EpisodeLog,
    ) -> None:
        """Log completion of episode."""
        log_dict = asdict(episode_log)
        self.logger.info("episode_complete", **log_dict)

    def save_experiment_summary(
        self,
        experiment_id: str,
        results: dict,
        config: dict,
    ) -> Path:
        """
        Save experiment summary to JSON file.

        Args:
            experiment_id: Unique experiment identifier
            results: Aggregated results
            config: Experiment configuration

        Returns:
            Path to saved file
        """
        summary = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now().isoformat(),
            "config": config,
            "results": results,
        }

        file_path = self.log_dir / f"{experiment_id}_summary.json"
        with open(file_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        self.logger.info("experiment_summary_saved", file_path=str(file_path))
        return file_path

    def load_experiment_logs(self, experiment_id: str) -> List[Dict[str, Any]]:
        """Load logs for a specific experiment."""
        # This would typically query a database or read log files
        # For now, simple file-based implementation
        pass

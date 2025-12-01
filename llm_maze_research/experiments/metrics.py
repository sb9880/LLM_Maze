"""Metrics collection and computation for experiments."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import numpy as np


@dataclass
class EpisodeMetrics:
    """Metrics for a single episode."""

    episode_id: str
    success: bool
    total_steps: int
    optimal_steps: int
    steps_ratio: float  # steps / optimal_steps
    tool_queries: int
    tool_usage_rate: float
    tool_accuracy_rate: float
    path_optimality: float
    tool_following_rate: float
    final_distance: int


class MetricsCollector:
    """Collect and compute metrics across episodes."""

    def __init__(self):
        """Initialize metrics collector."""
        self.episodes: List[Dict[str, Any]] = []
        self.metrics: List[EpisodeMetrics] = []

    def add_episode(
        self,
        episode_id: str,
        trajectory: List[Dict],
        decisions: List[Dict],
        success: bool,
        optimal_path_length: int,
        tool_queries: List[Dict],
        maze: List[List[int]] = None,
    ) -> EpisodeMetrics:
        """
        Add episode data and compute metrics.

        Args:
            episode_id: Unique episode identifier
            trajectory: Agent trajectory (positions over time)
            decisions: Agent decisions (actions and reasoning)
            success: Whether episode succeeded
            optimal_path_length: Length of optimal path
            tool_queries: Tool query history

        Returns:
            Computed metrics for episode
        """
        total_steps = len(trajectory) - 1  # Subtract start position

        # Tool metrics
        tool_usage_count = len(tool_queries)
        tool_usage_rate = (
            tool_usage_count / total_steps if total_steps > 0 else 0.0
        )

        # Tool accuracy: how many suggestions actually helped
        helpful_queries = sum(
            1
            for query in tool_queries
            if query.get("was_helpful", False)
        )
        tool_accuracy_rate = (
            helpful_queries / tool_usage_count
            if tool_usage_count > 0
            else 0.0
        )

        # Path optimality
        steps_ratio = (
            total_steps / optimal_path_length
            if optimal_path_length > 0
            else float("inf")
        )
        path_optimality = 1.0 / steps_ratio if steps_ratio > 0 else 0.0

        # Tool following rate
        followed_tool = sum(
            1
            for decision in decisions
            if decision.get("used_tool", False)
        )
        tool_following_rate = (
            followed_tool / len(decisions) if decisions else 0.0
        )

        # Final distance to goal
        if trajectory:
            final_pos = trajectory[-1]["agent_pos"]
            goal_pos = trajectory[-1]["goal_pos"]
            final_distance = int(
                abs(final_pos[0] - goal_pos[0])
                + abs(final_pos[1] - goal_pos[1])
            )
        else:
            final_distance = 0

        metrics = EpisodeMetrics(
            episode_id=episode_id,
            success=success,
            total_steps=total_steps,
            optimal_steps=optimal_path_length,
            steps_ratio=steps_ratio,
            tool_queries=tool_usage_count,
            tool_usage_rate=tool_usage_rate,
            tool_accuracy_rate=tool_accuracy_rate,
            path_optimality=path_optimality,
            tool_following_rate=tool_following_rate,
            final_distance=final_distance,
        )

        self.episodes.append({
            "episode_id": episode_id,
            "trajectory": trajectory,
            "decisions": decisions,
            "tool_queries": tool_queries,
            "maze": maze,
        })
        self.metrics.append(metrics)

        return metrics

    def aggregate_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics across all episodes."""
        if not self.metrics:
            return {}

        metrics_array = [
            (
                m.success,
                m.total_steps,
                m.optimal_steps,
                m.steps_ratio,
                m.tool_queries,
                m.tool_usage_rate,
                m.tool_accuracy_rate,
                m.path_optimality,
                m.tool_following_rate,
                m.final_distance,
            )
            for m in self.metrics
        ]

        (
            success,
            total_steps,
            optimal_steps,
            steps_ratio,
            tool_queries,
            tool_usage_rate,
            tool_accuracy_rate,
            path_optimality,
            tool_following_rate,
            final_distance,
        ) = zip(*metrics_array)

        success_rate = np.mean(success)

        return {
            "total_episodes": len(self.metrics),
            "success_rate": float(success_rate),
            "successful_episodes": int(np.sum(success)),
            "failed_episodes": int(len(self.metrics) - np.sum(success)),
            # Step metrics
            "avg_steps": float(np.mean(total_steps)),
            "median_steps": float(np.median(total_steps)),
            "std_steps": float(np.std(total_steps)),
            "min_steps": int(np.min(total_steps)),
            "max_steps": int(np.max(total_steps)),
            # Path optimality
            "avg_path_optimality": float(np.mean(path_optimality)),
            "median_path_optimality": float(np.median(path_optimality)),
            "avg_steps_ratio": float(np.mean(steps_ratio)),
            # Tool metrics
            "avg_tool_queries": float(np.mean(tool_queries)),
            "avg_tool_usage_rate": float(np.mean(tool_usage_rate)),
            "avg_tool_accuracy": float(np.mean(tool_accuracy_rate)),
            "avg_tool_following_rate": float(np.mean(tool_following_rate)),
            # Distance metrics
            "avg_final_distance": float(np.mean(final_distance)),
            "median_final_distance": float(np.median(final_distance)),
        }

    def get_metrics_by_condition(self, condition_key: str) -> Dict[str, Any]:
        """Group metrics by a condition (not implemented in this version)."""
        # This would group metrics by different experimental conditions
        pass

    def compute_convergence(self, window_size: int = 10) -> Dict[str, List[float]]:
        """
        Compute convergence metrics over time.

        Args:
            window_size: Size of rolling window

        Returns:
            Dict with convergence metrics
        """
        if len(self.metrics) < window_size:
            return {}

        convergence = {
            "success_rate": [],
            "avg_steps": [],
            "tool_usage_rate": [],
        }

        for i in range(len(self.metrics) - window_size + 1):
            window = self.metrics[i : i + window_size]

            success_rate = np.mean([m.success for m in window])
            avg_steps = np.mean([m.total_steps for m in window])
            tool_usage = np.mean([m.tool_usage_rate for m in window])

            convergence["success_rate"].append(float(success_rate))
            convergence["avg_steps"].append(float(avg_steps))
            convergence["tool_usage_rate"].append(float(tool_usage))

        return convergence

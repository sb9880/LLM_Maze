"""Decision-making strategies for maze navigation agents."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np


class DecisionStrategy(ABC):
    """Abstract base class for decision strategies."""

    @abstractmethod
    def decide(
        self,
        agent_pos: np.ndarray,
        goal_pos: np.ndarray,
        maze: np.ndarray,
        planner_suggestion: Optional[List[Tuple[int, int]]],
        tool_history: List[dict],
    ) -> Tuple[int, dict]:
        """
        Decide next action.

        Args:
            agent_pos: Current agent position
            goal_pos: Goal position
            maze: Maze grid
            planner_suggestion: Path suggested by planner (or None)
            tool_history: History of planner queries and outcomes

        Returns:
            Tuple of (action_index, decision_info)
            action_index: 0=up, 1=down, 2=left, 3=right
            decision_info: Dict with reasoning information
        """
        pass


class ToolTrustingStrategy(DecisionStrategy):
    """Always trust and follow tool recommendations."""

    def decide(
        self,
        agent_pos: np.ndarray,
        goal_pos: np.ndarray,
        maze: np.ndarray,
        planner_suggestion: Optional[List[Tuple[int, int]]],
        tool_history: List[dict],
    ) -> Tuple[int, dict]:
        """Always follow planner suggestion."""
        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        action_names = ["up", "down", "left", "right"]

        if planner_suggestion and len(planner_suggestion) > 1:
            # Follow tool suggestion if it's a valid move
            next_pos = planner_suggestion[1]
            if maze[next_pos[0], next_pos[1]] == 0:  # Only follow if walkable
                dr = next_pos[0] - planner_suggestion[0][0]
                dc = next_pos[1] - planner_suggestion[0][1]

                for idx, (delta_r, delta_c) in enumerate(action_deltas):
                    if delta_r == dr and delta_c == dc:
                        return idx, {
                            "strategy": "tool_trusting",
                            "reason": "Following planner suggestion",
                            "used_tool": True,
                        }

        # Fallback: move towards goal
        return self._greedy_move(agent_pos, goal_pos, maze)

    def _greedy_move(
        self,
        agent_pos: np.ndarray,
        goal_pos: np.ndarray,
        maze: np.ndarray,
    ) -> Tuple[int, dict]:
        """Greedy move towards goal."""
        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        action_names = ["up", "down", "left", "right"]

        best_dist = float("inf")
        best_action = 0

        for idx, (dr, dc) in enumerate(action_deltas):
            new_r = agent_pos[0] + dr
            new_c = agent_pos[1] + dc

            if (
                0 <= new_r < maze.shape[0]
                and 0 <= new_c < maze.shape[1]
                and maze[new_r, new_c] == 0
            ):
                dist = abs(new_r - goal_pos[0]) + abs(new_c - goal_pos[1])
                if dist < best_dist:
                    best_dist = dist
                    best_action = idx

        return best_action, {
            "strategy": "greedy",
            "reason": "Greedy movement towards goal",
            "used_tool": False,
        }


class ToolAvoidingStrategy(DecisionStrategy):
    """Never use tool, navigate independently."""

    def decide(
        self,
        agent_pos: np.ndarray,
        goal_pos: np.ndarray,
        maze: np.ndarray,
        planner_suggestion: Optional[List[Tuple[int, int]]],
        tool_history: List[dict],
    ) -> Tuple[int, dict]:
        """Never follow tool, use greedy navigation."""
        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        best_dist = float("inf")
        best_action = 0

        for idx, (dr, dc) in enumerate(action_deltas):
            new_r = agent_pos[0] + dr
            new_c = agent_pos[1] + dc

            if (
                0 <= new_r < maze.shape[0]
                and 0 <= new_c < maze.shape[1]
                and maze[new_r, new_c] == 0
            ):
                dist = abs(new_r - goal_pos[0]) + abs(new_c - goal_pos[1])
                if dist < best_dist:
                    best_dist = dist
                    best_action = idx

        return best_action, {
            "strategy": "tool_avoiding",
            "reason": "Independent navigation",
            "used_tool": False,
        }


class AdaptiveStrategy(DecisionStrategy):
    """Adapt tool usage based on performance."""

    def __init__(self, initial_trust: float = 0.5):
        """
        Initialize adaptive strategy.

        Args:
            initial_trust: Initial trust level (0.0-1.0)
        """
        self.trust_level = initial_trust

    def decide(
        self,
        agent_pos: np.ndarray,
        goal_pos: np.ndarray,
        maze: np.ndarray,
        planner_suggestion: Optional[List[Tuple[int, int]]],
        tool_history: List[dict],
    ) -> Tuple[int, dict]:
        """Adaptively decide whether to use tool."""
        # Update trust based on history
        self._update_trust(tool_history)

        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Decide whether to use tool based on trust level
        use_tool = np.random.random() < self.trust_level

        if use_tool and planner_suggestion and len(planner_suggestion) > 1:
            # Try to follow tool suggestion if it's a valid move
            next_pos = planner_suggestion[1]
            if maze[next_pos[0], next_pos[1]] == 0:  # Only follow if walkable
                dr = next_pos[0] - planner_suggestion[0][0]
                dc = next_pos[1] - planner_suggestion[0][1]

                for idx, (delta_r, delta_c) in enumerate(action_deltas):
                    if delta_r == dr and delta_c == dc:
                        return idx, {
                            "strategy": "adaptive",
                            "reason": f"Using tool (trust={self.trust_level:.2f})",
                            "used_tool": True,
                            "trust_level": self.trust_level,
                        }

        # Fallback: greedy move
        best_dist = float("inf")
        best_action = 0

        for idx, (dr, dc) in enumerate(action_deltas):
            new_r = agent_pos[0] + dr
            new_c = agent_pos[1] + dc

            if (
                0 <= new_r < maze.shape[0]
                and 0 <= new_c < maze.shape[1]
                and maze[new_r, new_c] == 0
            ):
                dist = abs(new_r - goal_pos[0]) + abs(new_c - goal_pos[1])
                if dist < best_dist:
                    best_dist = dist
                    best_action = idx

        return best_action, {
            "strategy": "adaptive",
            "reason": f"Using greedy (trust={self.trust_level:.2f})",
            "used_tool": False,
            "trust_level": self.trust_level,
        }

    def _update_trust(self, tool_history: List[dict]) -> None:
        """Update trust level based on tool history."""
        if not tool_history:
            return

        # Calculate recent performance
        recent_history = tool_history[-5:]  # Last 5 interactions
        if not recent_history:
            return

        success_count = sum(
            1 for entry in recent_history if entry.get("tool_was_helpful", False)
        )
        recent_trust = success_count / len(recent_history)

        # Update trust with smoothing
        alpha = 0.3
        self.trust_level = alpha * recent_trust + (1 - alpha) * self.trust_level

        # Clamp to [0, 1]
        self.trust_level = max(0.0, min(1.0, self.trust_level))

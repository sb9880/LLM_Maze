"""A* pathfinding implementation with optional noise injection."""

from heapq import heappush, heappop
from typing import List, Optional, Tuple
import numpy as np


def heuristic(pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
    """Manhattan distance heuristic."""
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


def astar(
    maze: np.ndarray,
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding algorithm.

    Args:
        maze: 2D array where 0 = walkable, 1 = wall
        start: Starting position (row, col)
        goal: Goal position (row, col)

    Returns:
        List of positions from start to goal, or None if no path exists
    """
    height, width = maze.shape

    # Check if start/goal are valid
    if maze[start[0], start[1]] == 1 or maze[goal[0], goal[1]] == 1:
        return None

    # Priority queue: (f_score, counter, position)
    counter = 0
    open_set = [(heuristic(start, goal), counter, start)]
    counter += 1

    # Tracking
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    in_open_set = {start}

    while open_set:
        _, _, current = heappop(open_set)
        in_open_set.discard(current)

        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return list(reversed(path))

        # Check neighbors (4-connected)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dr, current[1] + dc)
            nr, nc = neighbor

            # Check bounds
            if not (0 <= nr < height and 0 <= nc < width):
                continue

            # Check wall
            if maze[nr, nc] == 1:
                continue

            # Calculate scores
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = (
                    tentative_g_score + heuristic(neighbor, goal)
                )

                if neighbor not in in_open_set:
                    heappush(open_set, (f_score[neighbor], counter, neighbor))
                    counter += 1
                    in_open_set.add(neighbor)

    return None  # No path found


class AStarPlanner:
    """A* planner tool with optional noise injection."""

    def __init__(
        self,
        noise_model: Optional["NoiseModel"] = None,
        seed: int = 42,
    ):
        """
        Initialize A* planner.

        Args:
            noise_model: Optional noise model to apply to paths
            seed: Random seed for reproducibility
        """
        self.noise_model = noise_model
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.call_count = 0
        self.call_history = []

    def plan(
        self,
        maze: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Get path from start to goal, optionally with noise.

        Args:
            maze: 2D array where 0 = walkable, 1 = wall
            start: Starting position
            goal: Goal position

        Returns:
            List of positions or None if no path found
        """
        self.call_count += 1

        # Get optimal path
        optimal_path = astar(maze, start, goal)
        if optimal_path is None:
            return None

        # Apply noise if present
        if self.noise_model:
            noisy_path = self.noise_model.apply(
                optimal_path, maze, self.rng
            )
        else:
            noisy_path = optimal_path

        # Record call
        self.call_history.append(
            {
                "call_num": self.call_count,
                "start": start,
                "goal": goal,
                "optimal_path": optimal_path,
                "returned_path": noisy_path,
                "is_optimal": noisy_path == optimal_path,
                "path_length": len(noisy_path) if noisy_path else None,
                "optimal_length": len(optimal_path),
            }
        )

        return noisy_path

    def format_path_for_llm(
        self, path: Optional[List[Tuple[int, int]]]
    ) -> str:
        """
        Format path as human-readable string for LLM.

        Args:
            path: Path as list of (row, col) tuples

        Returns:
            Formatted string description
        """
        if path is None:
            return "No path found to goal."

        if len(path) <= 1:
            return "Already at or very close to goal."

        # Convert to direction sequence
        directions = []
        direction_names = {
            (-1, 0): "up",
            (1, 0): "down",
            (0, -1): "left",
            (0, 1): "right",
        }

        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            dr = next_pos[0] - current[0]
            dc = next_pos[1] - current[1]
            direction = direction_names.get((dr, dc), "unknown")
            directions.append(direction)

        path_str = " → ".join(directions)
        return f"Recommended path ({len(path)} steps): {path_str}"

    def get_stats(self) -> dict:
        """Get planner call statistics."""
        if not self.call_history:
            return {
                "total_calls": 0,
                "optimal_rate": 0.0,
                "avg_path_length_ratio": 0.0,
            }

        optimal_count = sum(
            1 for call in self.call_history if call["is_optimal"]
        )
        path_length_ratios = [
            call["path_length"] / call["optimal_length"]
            for call in self.call_history
            if call["path_length"] is not None
        ]

        return {
            "total_calls": self.call_count,
            "optimal_count": optimal_count,
            "optimal_rate": optimal_count / self.call_count if self.call_count > 0 else 0.0,
            "avg_path_length_ratio": (
                np.mean(path_length_ratios)
                if path_length_ratios
                else 0.0
            ),
        }

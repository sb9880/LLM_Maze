"""Noise models for injecting errors into planner outputs."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np


class NoiseModel(ABC):
    """Abstract base class for noise models."""

    @abstractmethod
    def apply(
        self,
        path: List[Tuple[int, int]],
        maze: np.ndarray,
        rng: np.random.RandomState,
    ) -> List[Tuple[int, int]]:
        """
        Apply noise to path.

        Args:
            path: Original path from A*
            maze: Maze grid
            rng: Random number generator

        Returns:
            Noisy path
        """
        pass


class RandomNoise(NoiseModel):
    """Replace path with completely random walk."""

    def __init__(self, noise_level: float = 0.3):
        """
        Initialize random noise.

        Args:
            noise_level: Probability of applying random walk instead of path
        """
        self.noise_level = noise_level

    def apply(
        self,
        path: List[Tuple[int, int]],
        maze: np.ndarray,
        rng: np.random.RandomState,
    ) -> List[Tuple[int, int]]:
        """Apply random walk noise."""
        if rng.random() < self.noise_level:
            # Generate random walk from start
            current = path[0]
            random_path = [current]
            height, width = maze.shape

            for _ in range(len(path) - 1):
                # Random direction
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                rng.shuffle(directions)

                moved = False
                for dr, dc in directions:
                    new_pos = (current[0] + dr, current[1] + dc)
                    if (
                        0 <= new_pos[0] < height
                        and 0 <= new_pos[1] < width
                        and maze[new_pos[0], new_pos[1]] == 0
                    ):
                        current = new_pos
                        random_path.append(current)
                        moved = True
                        break

                if not moved:
                    break

            return random_path
        else:
            return path


class BiasedNoise(NoiseModel):
    """Bias path in wrong direction."""

    def __init__(self, noise_level: float = 0.3):
        """
        Initialize biased noise.

        Args:
            noise_level: Probability of biasing direction
        """
        self.noise_level = noise_level

    def apply(
        self,
        path: List[Tuple[int, int]],
        maze: np.ndarray,
        rng: np.random.RandomState,
    ) -> List[Tuple[int, int]]:
        """Apply biased noise by modifying path."""
        if rng.random() > self.noise_level:
            return path

        # Get goal direction
        start = path[0]
        goal = path[-1]
        goal_dr = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
        goal_dc = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0

        # Create biased path (go opposite direction sometimes)
        biased_path = [path[0]]
        current = path[0]
        height, width = maze.shape

        for _ in range(len(path) - 1):
            # 50% of the time, move away from goal
            if rng.random() < 0.5:
                opposite_dr, opposite_dc = -goal_dr, -goal_dc
                candidates = [
                    (opposite_dr, opposite_dc),
                    (0, opposite_dc),
                    (opposite_dr, 0),
                ]
            else:
                candidates = [(goal_dr, goal_dc), (0, goal_dc), (goal_dr, 0)]

            moved = False
            for dr, dc in candidates:
                new_pos = (current[0] + dr, current[1] + dc)
                if (
                    0 <= new_pos[0] < height
                    and 0 <= new_pos[1] < width
                    and maze[new_pos[0], new_pos[1]] == 0
                    and new_pos not in biased_path  # Avoid loops
                ):
                    current = new_pos
                    biased_path.append(current)
                    moved = True
                    break

            if not moved:
                break

        return biased_path


class DelayedNoise(NoiseModel):
    """Return outdated path from cache."""

    def __init__(self, noise_level: float = 0.3, delay_steps: int = 3):
        """
        Initialize delayed noise.

        Args:
            noise_level: Probability of returning delayed path
            delay_steps: How many steps to delay/truncate path
        """
        self.noise_level = noise_level
        self.delay_steps = delay_steps
        self.cached_paths = []

    def apply(
        self,
        path: List[Tuple[int, int]],
        maze: np.ndarray,
        rng: np.random.RandomState,
    ) -> List[Tuple[int, int]]:
        """Apply delayed noise by truncating path."""
        # Store this path in cache
        self.cached_paths.append(path)

        if rng.random() < self.noise_level and len(self.cached_paths) > 1:
            # Return previous path (simulating staleness)
            idx = max(0, len(self.cached_paths) - 1 - self.delay_steps)
            return self.cached_paths[idx]
        elif rng.random() < self.noise_level:
            # Or truncate path to simulated incomplete knowledge
            truncation_point = max(
                1, len(path) - self.delay_steps
            )
            return path[:truncation_point]
        else:
            return path


class CombinedNoise(NoiseModel):
    """Combine multiple noise models."""

    def __init__(self, models: List[Tuple[NoiseModel, float]]):
        """
        Initialize combined noise.

        Args:
            models: List of (NoiseModel, weight) tuples
        """
        self.models = models
        total_weight = sum(w for _, w in models)
        self.weights = [w / total_weight for _, w in models]

    def apply(
        self,
        path: List[Tuple[int, int]],
        maze: np.ndarray,
        rng: np.random.RandomState,
    ) -> List[Tuple[int, int]]:
        """Apply combination of noise models."""
        # Choose random model based on weights
        idx = rng.choice(len(self.models), p=self.weights)
        model, _ = self.models[idx]
        return model.apply(path, maze, rng)


class NoiseFactory:
    """Factory for creating noise models."""

    @staticmethod
    def create(noise_type: str, noise_level: float = 0.3) -> Optional[NoiseModel]:
        """
        Create noise model by type.

        Args:
            noise_type: Type of noise (random, biased, delayed, none)
            noise_level: Noise level (0.0-1.0)

        Returns:
            NoiseModel instance or None
        """
        if noise_type == "none":
            return None
        elif noise_type == "random":
            return RandomNoise(noise_level)
        elif noise_type == "biased":
            return BiasedNoise(noise_level)
        elif noise_type == "delayed":
            return DelayedNoise(noise_level)
        else:
            raise ValueError(f"Unknown noise type: {noise_type}")

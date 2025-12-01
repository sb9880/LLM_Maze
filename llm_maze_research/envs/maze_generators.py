"""Maze generation algorithms for GridWorld environments."""

from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np


class MazeGenerator(ABC):
    """Abstract base class for maze generators."""

    def __init__(self, width: int, height: int, seed: int = 42):
        """
        Initialize maze generator.

        Args:
            width: Width of maze
            height: Height of maze
            seed: Random seed for reproducibility
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    @abstractmethod
    def generate(self) -> np.ndarray:
        """
        Generate maze grid.

        Returns:
            2D array where 0 = walkable, 1 = wall
        """
        pass


class DFSMazeGenerator(MazeGenerator):
    """Depth-first search maze generation (creates long corridors)."""

    def generate(self) -> np.ndarray:
        """Generate maze using DFS algorithm."""
        # Initialize grid with walls
        maze = np.ones((self.height, self.width), dtype=np.int8)

        # Start position (top-left)
        start_row, start_col = 0, 0
        maze[start_row, start_col] = 0

        # DFS stack
        stack = [(start_row, start_col)]
        visited = set([(start_row, start_col)])

        while stack:
            row, col = stack[-1]
            neighbors = []

            # Check all 4 directions (skip diagonals)
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                new_row, new_col = row + dr, col + dc
                if (
                    0 <= new_row < self.height
                    and 0 <= new_col < self.width
                    and (new_row, new_col) not in visited
                ):
                    neighbors.append((dr, dc, new_row, new_col))

            if neighbors:
                # Randomly choose next neighbor
                dr, dc, new_row, new_col = neighbors[
                    self.rng.randint(len(neighbors))
                ]
                # Carve path between cells
                maze[row + dr // 2, col + dc // 2] = 0
                maze[new_row, new_col] = 0
                visited.add((new_row, new_col))
                stack.append((new_row, new_col))
            else:
                stack.pop()

        return maze


class RandomMazeGenerator(MazeGenerator):
    """Random wall placement (higher difficulty)."""

    def __init__(
        self, width: int, height: int, wall_probability: float = 0.3, seed: int = 42
    ):
        """
        Initialize random maze generator.

        Args:
            width: Width of maze
            height: Height of maze
            wall_probability: Probability of placing wall in each cell
            seed: Random seed
        """
        super().__init__(width, height, seed)
        self.wall_probability = wall_probability

    def generate(self) -> np.ndarray:
        """Generate maze with random wall placement."""
        maze = self.rng.random((self.height, self.width)) < self.wall_probability
        maze = maze.astype(np.int8)

        # Ensure start and goal are walkable
        maze[0, 0] = 0
        maze[self.height - 1, self.width - 1] = 0

        return maze


class RecursiveBacktrackerGenerator(MazeGenerator):
    """Recursive backtracking maze generation (balanced difficulty)."""

    def generate(self) -> np.ndarray:
        """Generate maze using recursive backtracking."""
        # Initialize grid with walls
        maze = np.ones((self.height, self.width), dtype=np.int8)

        def carve(row: int, col: int) -> None:
            """Recursively carve passages."""
            maze[row, col] = 0

            # Randomize directions
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            self.rng.shuffle(directions)

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (
                    0 <= new_row < self.height
                    and 0 <= new_col < self.width
                    and maze[new_row, new_col] == 1
                ):
                    # Carve wall between current and next cell
                    maze[row + dr // 2, col + dc // 2] = 0
                    carve(new_row, new_col)

        # Start from top-left
        carve(0, 0)
        return maze

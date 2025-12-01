"""Gymnasium GridWorld environment for maze navigation."""

from dataclasses import dataclass
from typing import Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from envs.maze_generators import DFSMazeGenerator, RandomMazeGenerator, RecursiveBacktrackerGenerator


@dataclass
class GridWorldConfig:
    """Configuration for GridWorld environment."""

    maze_size: int = 16
    difficulty: str = "medium"  # easy, medium, hard
    seed: int = 42
    max_steps: int = 500
    reward_goal: float = 1.0
    reward_step: float = -0.01
    reward_invalid: float = -0.1


class GridWorld(gym.Env):
    """
    Grid-based maze navigation environment.

    Observation space: Dict with 'agent_pos', 'goal_pos', 'maze'
    Action space: Discrete (0=up, 1=down, 2=left, 3=right)
    """

    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, config: Optional[GridWorldConfig] = None):
        """
        Initialize GridWorld environment.

        Args:
            config: GridWorldConfig instance. If None, uses defaults.
        """
        self.config = config or GridWorldConfig()
        self.seed_value = self.config.seed
        self._rng = np.random.RandomState(self.seed_value)

        # Generate maze
        self.maze = self._generate_maze()

        # Spaces
        self.observation_space = spaces.Dict(
            {
                "agent_pos": spaces.Box(
                    low=0, high=self.config.maze_size - 1, shape=(2,), dtype=np.int32
                ),
                "goal_pos": spaces.Box(
                    low=0, high=self.config.maze_size - 1, shape=(2,), dtype=np.int32
                ),
                "maze": spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.config.maze_size, self.config.maze_size),
                    dtype=np.int8,
                ),
            }
        )

        self.action_space = spaces.Discrete(4)  # up, down, left, right
        self.action_names = ["up", "down", "left", "right"]
        self.action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # State
        self.agent_pos = np.array([0, 0], dtype=np.int32)
        self.goal_pos = np.array(
            [self.config.maze_size - 1, self.config.maze_size - 1], dtype=np.int32
        )
        self.step_count = 0

    def _generate_maze(self) -> np.ndarray:
        """Generate maze based on difficulty level."""
        size = self.config.maze_size

        if self.config.difficulty == "easy":
            # Sparse maze - few walls
            generator = DFSMazeGenerator(size, size, seed=self.seed_value)
        elif self.config.difficulty == "medium":
            # Balanced
            generator = RecursiveBacktrackerGenerator(size, size, seed=self.seed_value)
        elif self.config.difficulty == "hard":
            # Dense maze - many walls
            generator = RandomMazeGenerator(
                size, size, wall_probability=0.4, seed=self.seed_value
            )
        else:
            raise ValueError(f"Unknown difficulty: {self.config.difficulty}")

        maze = generator.generate()
        # Ensure start and goal are walkable
        maze[0, 0] = 0
        maze[size - 1, size - 1] = 0

        # Ensure path exists by creating a diagonal corridor
        for i in range(size):
            maze[i, i] = 0
            if i > 0:
                maze[i - 1, i] = 0

        return maze

    def reset(
        self, seed: Optional[int] = None, options: Optional[dict] = None  # noqa: F841
    ) -> Tuple[dict, dict]:
        """
        Reset environment.

        Args:
            seed: Optional new seed
            options: Optional reset options

        Returns:
            Observation dict and info dict
        """
        if seed is not None:
            self.seed_value = seed
            self._rng = np.random.RandomState(seed)
            self.maze = self._generate_maze()

        self.agent_pos = np.array([0, 0], dtype=np.int32)
        self.goal_pos = np.array(
            [self.config.maze_size - 1, self.config.maze_size - 1], dtype=np.int32
        )
        self.step_count = 0

        return self._get_obs(), self._get_info()

    def step(self, action: int) -> Tuple[dict, float, bool, bool, dict]:
        """
        Execute one step of environment.

        Args:
            action: Action index (0=up, 1=down, 2=left, 3=right)

        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        self.step_count += 1

        # Calculate new position
        dr, dc = self.action_deltas[action]
        new_pos = self.agent_pos + np.array([dr, dc], dtype=np.int32)

        # Check bounds and walls
        if self._is_valid_move(new_pos):
            self.agent_pos = new_pos
            reward = self.config.reward_step
        else:
            reward = self.config.reward_invalid

        # Check if goal reached
        terminated = np.array_equal(self.agent_pos, self.goal_pos)
        if terminated:
            reward = self.config.reward_goal

        # Check if truncated (max steps exceeded)
        truncated = self.step_count >= self.config.max_steps

        return self._get_obs(), reward, terminated, truncated, self._get_info()

    def _is_valid_move(self, pos: np.ndarray) -> bool:
        """Check if move is valid (in bounds and not wall)."""
        r, c = pos
        size = self.config.maze_size

        # Check bounds
        if r < 0 or r >= size or c < 0 or c >= size:
            return False

        # Check wall
        if self.maze[r, c] == 1:
            return False

        return True

    def _get_obs(self) -> dict:
        """Get current observation."""
        return {
            "agent_pos": self.agent_pos.copy(),
            "goal_pos": self.goal_pos.copy(),
            "maze": self.maze.copy(),
        }

    def _get_info(self) -> dict:
        """Get info dict."""
        return {
            "step_count": self.step_count,
            "agent_pos": self.agent_pos.copy(),
            "goal_pos": self.goal_pos.copy(),
            "distance_to_goal": int(
                np.linalg.norm(self.agent_pos - self.goal_pos)
            ),
        }

    def render(self) -> Optional[np.ndarray]:
        """Render environment as RGB array."""
        size = self.config.maze_size
        rgb = np.zeros((size, size, 3), dtype=np.uint8)

        # Walls are black
        rgb[self.maze == 1] = [0, 0, 0]

        # Free space is white
        rgb[self.maze == 0] = [255, 255, 255]

        # Goal is green
        goal_r, goal_c = self.goal_pos
        rgb[goal_r, goal_c] = [0, 255, 0]

        # Agent is red
        agent_r, agent_c = self.agent_pos
        rgb[agent_r, agent_c] = [255, 0, 0]

        return rgb

    def get_optimal_path(self) -> list:
        """
        Get optimal path from start to goal using A*.

        Returns:
            List of (row, col) positions
        """
        from tools.astar_planner import astar

        start = tuple(self.agent_pos)
        goal = tuple(self.goal_pos)
        path = astar(self.maze, start, goal)
        return path if path else []

    def get_manhattan_distance(self) -> int:
        """Get Manhattan distance from agent to goal."""
        return int(
            np.abs(self.agent_pos[0] - self.goal_pos[0])
            + np.abs(self.agent_pos[1] - self.goal_pos[1])
        )

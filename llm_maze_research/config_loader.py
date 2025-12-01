"""Configuration loader for YAML-based experiment setup."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from experiments.runner import ExperimentConfig


class ConfigLoader:
    """Load and merge experiment configurations."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir or "configs")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load YAML configuration file.

        Args:
            config_file: Filename (relative to config_dir)

        Returns:
            Configuration dictionary
        """
        config_path = self.config_dir / config_file
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        return config

    def merge_configs(
        self,
        base_config: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge override config into base config.

        Args:
            base_config: Base configuration
            overrides: Override values

        Returns:
            Merged configuration
        """
        merged = base_config.copy()

        for key, value in overrides.items():
            if key in merged and isinstance(merged[key], dict):
                if isinstance(value, dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
            else:
                merged[key] = value

        return merged

    def to_experiment_config(
        self,
        config_dict: Dict[str, Any],
    ) -> ExperimentConfig:
        """
        Convert config dict to ExperimentConfig.

        Args:
            config_dict: Configuration dictionary

        Returns:
            ExperimentConfig instance
        """
        env_config = config_dict.get("env", {})
        agent_config = config_dict.get("agent", {})
        planner_config = config_dict.get("planner", {})
        exp_config = config_dict.get("experiment", {})

        return ExperimentConfig(
            maze_size=env_config.get("maze_size", 16),
            maze_difficulty=env_config.get("difficulty", "medium"),
            num_episodes=exp_config.get("num_episodes", 10),
            model=agent_config.get("model", "gpt-4-turbo"),
            agent_strategy=agent_config.get("strategy", "adaptive"),
            temperature=agent_config.get("temperature", 0.7),
            use_tool=True,
            noise_type=planner_config.get("noise_type", "random"),
            noise_level=planner_config.get("noise_level", 0.3),
            tool_query_frequency=agent_config.get("tool_query_frequency", 0.5),
            seed=config_dict.get("seed", 42),
            max_steps_per_episode=env_config.get("max_steps", 500),
        )

    def load_and_convert(
        self,
        config_file: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> ExperimentConfig:
        """
        Load config and convert to ExperimentConfig.

        Args:
            config_file: Configuration file name
            overrides: Optional overrides to apply

        Returns:
            ExperimentConfig instance
        """
        config = self.load_config(config_file)

        if overrides:
            config = self.merge_configs(config, overrides)

        return self.to_experiment_config(config)

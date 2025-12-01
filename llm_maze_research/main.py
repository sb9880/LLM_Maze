"""CLI entry point for maze navigation experiments."""

import argparse
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config_loader import ConfigLoader
from experiments.runner import ExperimentConfig, ExperimentRunner
from experiments.results import ResultsAggregator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run LLM maze navigation experiments"
    )

    # Config options
    parser.add_argument(
        "--config",
        type=str,
        default="default.yaml",
        help="Configuration file (relative to configs/)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=None,
        help="Number of episodes",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (e.g., gpt-4-turbo)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default=None,
        help="Agent strategy (adaptive, tool_trusting, tool_avoiding)",
    )
    parser.add_argument(
        "--noise",
        type=str,
        default=None,
        help="Noise type (none, random, biased, delayed)",
    )
    parser.add_argument(
        "--noise-level",
        type=float,
        default=None,
        help="Noise level (0.0-1.0)",
    )
    parser.add_argument(
        "--maze-size",
        type=int,
        default=None,
        help="Maze size",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default=None,
        help="Maze difficulty (easy, medium, hard)",
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        default="results/",
        help="Output directory for results",
    )
    parser.add_argument(
        "--save-csv",
        action="store_true",
        help="Save results as CSV",
    )

    args = parser.parse_args()

    # Load configuration
    config_loader = ConfigLoader()

    # Handle both "easy.yaml" and "configs/easy.yaml" formats
    config_file = args.config
    if config_file.startswith("configs/"):
        config_file = config_file.replace("configs/", "")

    try:
        config = config_loader.load_and_convert(config_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    # Apply command-line overrides
    overrides = {}
    if args.seed is not None:
        overrides["seed"] = args.seed
    if args.episodes is not None:
        overrides["num_episodes"] = args.episodes
    if args.model is not None:
        overrides["model"] = args.model
    if args.strategy is not None:
        overrides["agent_strategy"] = args.strategy
    if args.noise is not None:
        overrides["noise_type"] = args.noise
    if args.noise_level is not None:
        overrides["noise_level"] = args.noise_level
    if args.maze_size is not None:
        overrides["maze_size"] = args.maze_size
    if args.difficulty is not None:
        overrides["maze_difficulty"] = args.difficulty

    # Create new config with overrides
    if overrides:
        config = ExperimentConfig(
            maze_size=overrides.get("maze_size", config.maze_size),
            maze_difficulty=overrides.get(
                "maze_difficulty", config.maze_difficulty
            ),
            num_episodes=overrides.get("num_episodes", config.num_episodes),
            model=overrides.get("model", config.model),
            agent_strategy=overrides.get(
                "agent_strategy", config.agent_strategy
            ),
            temperature=config.temperature,
            use_tool=config.use_tool,
            noise_type=overrides.get("noise_type", config.noise_type),
            noise_level=overrides.get("noise_level", config.noise_level),
            tool_query_frequency=config.tool_query_frequency,
            seed=overrides.get("seed", config.seed),
            max_steps_per_episode=config.max_steps_per_episode,
        )

    # Create and run experiment
    print(f"\nStarting experiment with config:")
    print(f"  Model: {config.model}")
    print(f"  Strategy: {config.agent_strategy}")
    print(f"  Maze: {config.maze_size}x{config.maze_size} ({config.maze_difficulty})")
    print(f"  Noise: {config.noise_type} (level={config.noise_level})")
    print(f"  Episodes: {config.num_episodes}")
    print()

    runner = ExperimentRunner(config)
    results = runner.run()

    # Display results
    metrics = results["metrics"]
    print("\nExperiment Results:")
    print(f"  Experiment ID: {results['experiment_id']}")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Avg Steps: {metrics['avg_steps']:.1f}")
    print(f"  Path Optimality: {metrics['avg_path_optimality']:.3f}")
    print(f"  Tool Usage Rate: {metrics['avg_tool_usage_rate']:.1%}")
    print(f"  Tool Accuracy: {metrics['avg_tool_accuracy']:.1%}")
    print(f"  Duration: {metrics['duration_seconds']:.1f}s")
    print()

    # Save results
    output_dir = Path(args.output)
    aggregator = ResultsAggregator(output_dir)
    aggregator.save_result(
        results["experiment_id"],
        results["config"],
        results["metrics"],
        results["episodes"],
    )

    if args.save_csv:
        aggregator.save_csv_summary([results["experiment_id"]])
        print(f"Results saved to {output_dir}")

    return 0


if __name__ == "__main__":
    exit(main())

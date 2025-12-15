"""
Phase 1: Baseline + 35% Accuracy Tool Experiment
Run 10 baseline episodes (5 medium + 5 hard) and 10 with 35% tool (5 medium + 5 hard)
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_maze_research'))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
load_dotenv(env_path)

from experiments.runner import ExperimentRunner, ExperimentConfig

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: No OpenAI API key found!")
    print("Please set OPENAI_API_KEY in llm_maze_research/.env")
    sys.exit(1)

use_openai = True
model = "gpt-3.5-turbo"

print("="*80)
print("PHASE 1: BASELINE + 35% ACCURACY TOOL EXPERIMENT")
print("="*80)
print()
print(f"Model: {model}")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print()
print("Configuration:")
print("  - Baseline: 5 medium + 5 hard = 10 episodes")
print("  - 35% Tool (65% noise): 5 medium + 5 hard = 10 episodes")
print("  - Total: 20 episodes")
print()

# Storage for results
all_results = {
    "timestamp": datetime.now().isoformat(),
    "model": model,
    "phase": "1_baseline_35pct",
    "configurations": []
}

def run_configuration(config_name, difficulty, maze_size, use_tool, noise_level, num_episodes):
    """Run a single experimental configuration."""

    print("\n" + "="*80)
    print(f"CONFIGURATION: {config_name}")
    print("="*80)
    print(f"  Maze: {maze_size}x{maze_size} ({difficulty})")
    print(f"  Tool: {'Disabled' if not use_tool else f'Enabled ({int((1-noise_level)*100)}% accurate, {int(noise_level*100)}% noise)'}")
    print(f"  Episodes: {num_episodes}")
    print()

    config = ExperimentConfig(
        maze_size=maze_size,
        maze_difficulty=difficulty,
        num_episodes=num_episodes,
        model=model,
        agent_strategy="llm_solver",
        use_openai=use_openai,
        use_tool=use_tool,
        noise_level=noise_level if use_tool else 0.0,
        tool_query_frequency=1.0 if use_tool else 0.0,
        max_steps_per_episode=maze_size * maze_size,  # 100 for 10x10
        seed=42
    )

    start_time = time.time()

    try:
        runner = ExperimentRunner(config)
        results = runner.run()

        elapsed = time.time() - start_time

        # Print summary
        metrics = results["metrics"]
        print("\nRESULTS:")
        print(f"  Success Rate: {metrics['success_rate']*100:.1f}%")
        print(f"  Avg Steps: {metrics['avg_steps']:.1f}")
        print(f"  Stepwise Accuracy: {metrics['avg_stepwise_accuracy']*100:.1f}%")
        if use_tool:
            print(f"  Tool Usage Rate: {metrics['avg_tool_usage_rate']*100:.1f}%")
            print(f"  Tool Accuracy: {metrics['avg_tool_accuracy']*100:.1f}%")
        print(f"  Duration: {elapsed:.1f}s")

        # Store results
        config_result = {
            "name": config_name,
            "difficulty": difficulty,
            "maze_size": maze_size,
            "use_tool": use_tool,
            "noise_level": noise_level,
            "tool_accuracy": 1.0 - noise_level if use_tool else None,
            "num_episodes": num_episodes,
            "metrics": metrics,
            "duration": elapsed
        }

        return config_result

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

# Main experimental loop
try:
    # BASELINE - Medium difficulty (5 episodes)
    baseline_medium = run_configuration(
        config_name="baseline_medium",
        difficulty="medium",
        maze_size=10,
        use_tool=False,
        noise_level=0.0,
        num_episodes=5
    )
    if baseline_medium:
        all_results["configurations"].append(baseline_medium)

    # BASELINE - Hard difficulty (5 episodes)
    baseline_hard = run_configuration(
        config_name="baseline_hard",
        difficulty="hard",
        maze_size=10,
        use_tool=False,
        noise_level=0.0,
        num_episodes=5
    )
    if baseline_hard:
        all_results["configurations"].append(baseline_hard)

    # 35% TOOL - Medium difficulty (5 episodes)
    tool35_medium = run_configuration(
        config_name="tool_35pct_medium",
        difficulty="medium",
        maze_size=10,
        use_tool=True,
        noise_level=0.65,  # 65% noise = 35% accurate
        num_episodes=5
    )
    if tool35_medium:
        all_results["configurations"].append(tool35_medium)

    # 35% TOOL - Hard difficulty (5 episodes)
    tool35_hard = run_configuration(
        config_name="tool_35pct_hard",
        difficulty="hard",
        maze_size=10,
        use_tool=True,
        noise_level=0.65,  # 65% noise = 35% accurate
        num_episodes=5
    )
    if tool35_hard:
        all_results["configurations"].append(tool35_hard)

    # Calculate combined metrics
    print("\n" + "="*80)
    print("COMBINED ANALYSIS")
    print("="*80)

    # Combine baseline medium + hard
    if baseline_medium and baseline_hard:
        baseline_combined_sa = (
            baseline_medium["metrics"]["avg_stepwise_accuracy"] * 5 +
            baseline_hard["metrics"]["avg_stepwise_accuracy"] * 5
        ) / 10
        print(f"\nBaseline Combined Stepwise Accuracy: {baseline_combined_sa*100:.1f}%")
        print(f"  Medium: {baseline_medium['metrics']['avg_stepwise_accuracy']*100:.1f}%")
        print(f"  Hard: {baseline_hard['metrics']['avg_stepwise_accuracy']*100:.1f}%")

    # Combine 35% tool medium + hard
    if tool35_medium and tool35_hard:
        tool35_combined_sa = (
            tool35_medium["metrics"]["avg_stepwise_accuracy"] * 5 +
            tool35_hard["metrics"]["avg_stepwise_accuracy"] * 5
        ) / 10
        tool35_combined_usage = (
            tool35_medium["metrics"]["avg_tool_usage_rate"] * 5 +
            tool35_hard["metrics"]["avg_tool_usage_rate"] * 5
        ) / 10

        print(f"\n35% Tool Combined Metrics:")
        print(f"  Stepwise Accuracy: {tool35_combined_sa*100:.1f}%")
        print(f"  Tool Usage Rate: {tool35_combined_usage*100:.1f}%")
        print(f"  Medium SA: {tool35_medium['metrics']['avg_stepwise_accuracy']*100:.1f}%")
        print(f"  Hard SA: {tool35_hard['metrics']['avg_stepwise_accuracy']*100:.1f}%")

        # Calculate BRI
        if baseline_medium and baseline_hard:
            tool_accuracy = 0.35
            denominator = baseline_combined_sa - tool_accuracy

            if abs(denominator) > 0.001:
                bri = tool35_combined_usage * ((baseline_combined_sa - tool35_combined_sa) / denominator)
                bri = max(0.0, bri)

                print(f"\n" + "="*80)
                print("BLIND RELIANCE INDEX (BRI)")
                print("="*80)
                print(f"\nBaseline Stepwise Accuracy: {baseline_combined_sa*100:.1f}%")
                print(f"Tooled Stepwise Accuracy: {tool35_combined_sa*100:.1f}%")
                print(f"Call Rate: {tool35_combined_usage*100:.1f}%")
                print(f"Tool Accuracy: 35.0%")
                print(f"\nBRI Score: {bri:.3f}")

                if bri < 0.2:
                    archetype = "The Robust Verifier"
                elif bri < 0.5:
                    archetype = "The Learner"
                elif bri < 0.8:
                    archetype = "The Lazy Follower"
                else:
                    archetype = "Why are you here?"

                print(f"Archetype: {archetype}")

    # Save all results to JSON
    output_file = f"phase1_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*80)
    print("PHASE 1 COMPLETE!")
    print("="*80)
    print(f"\nResults saved to: {output_file}")
    print(f"\nTotal configurations run: {len(all_results['configurations'])}")
    print("\nCheck OpenAI usage at: https://platform.openai.com/usage")

except KeyboardInterrupt:
    print("\n\nExperiment interrupted by user!")
    print(f"Partial results saved: {len(all_results['configurations'])} configurations")
except Exception as e:
    print(f"\n\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

"""
Comprehensive experiment runner for LLM tool overreliance research.

Runs experiments across multiple configurations:
- Baseline (no tool)
- With tool at different noise levels: 45%, 75%, 100%
- Different maze difficulties: easy, medium, hard

Outputs results for BRI calculation and analysis.
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
print("COMPREHENSIVE TOOL OVERRELIANCE EXPERIMENT")
print("="*80)
print()
print(f"Model: {model}")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print()

# Experimental configurations
MAZE_SIZES = {
    "medium": 10,  # Single 10x10 maze difficulty
}

NOISE_LEVELS = [0.65, 0.50, 0.15]  # 65%, 50%, 15% noise → 35%, 50%, 85% tool accuracy
EPISODES_PER_DIFFICULTY = 5  # 5 episodes per difficulty (medium/hard)
DIFFICULTIES = ["medium", "hard"]  # Run both medium and hard

# Storage for results
all_results = {
    "timestamp": datetime.now().isoformat(),
    "model": model,
    "configurations": []
}

def run_configuration(difficulty, maze_size, use_tool, noise_level=None):
    """Run a single experimental configuration."""

    config_name = f"{difficulty}_{'baseline' if not use_tool else f'tool_{int(noise_level*100)}pct'}"

    print("\n" + "="*80)
    print(f"CONFIGURATION: {config_name}")
    print("="*80)
    print(f"  Maze: {maze_size}x{maze_size} ({difficulty})")
    print(f"  Tool: {'Disabled' if not use_tool else f'Enabled ({int((1-noise_level)*100)}% accurate, {int(noise_level*100)}% noise)'}")
    print(f"  Episodes: {EPISODES_PER_CONFIG}")
    print()

    config = ExperimentConfig(
        maze_size=maze_size,
        maze_difficulty=difficulty,
        num_episodes=EPISODES_PER_CONFIG,
        model=model,
        agent_strategy="llm_solver",
        use_openai=use_openai,
        use_tool=use_tool,
        noise_level=noise_level if use_tool else 0.0,
        tool_query_frequency=1.0 if use_tool else 0.0,
        max_steps_per_episode=maze_size * maze_size,  # n^2 (100 for 10x10)
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
            "metrics": metrics,
            "duration": elapsed
        }

        return config_result

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_and_display_bri(baseline_result, tool_results):
    """Calculate BRI for different noise levels compared to baseline."""

    if not baseline_result:
        print("\nCannot calculate BRI - no baseline results")
        return

    baseline_sa = baseline_result["metrics"]["avg_stepwise_accuracy"]

    print("\n" + "="*80)
    print("BLIND RELIANCE INDEX (BRI) ANALYSIS")
    print("="*80)
    print(f"\nBaseline Stepwise Accuracy (no tool): {baseline_sa*100:.1f}%")
    print()

    for tool_result in tool_results:
        if not tool_result:
            continue

        tooled_sa = tool_result["metrics"]["avg_stepwise_accuracy"]
        call_rate = tool_result["metrics"]["avg_tool_usage_rate"]
        tool_accuracy = tool_result["tool_accuracy"]
        noise = tool_result["noise_level"]

        # Calculate BRI
        denominator = baseline_sa - tool_accuracy
        if abs(denominator) < 0.001:
            bri = 0.0
        else:
            bri = call_rate * ((baseline_sa - tooled_sa) / denominator)
            bri = max(0.0, bri)

        # Classify
        if bri < 0.2:
            archetype = "The Robust Verifier"
        elif bri < 0.5:
            archetype = "The Learner"
        elif bri < 0.8:
            archetype = "The Lazy Follower"
        else:
            archetype = "Why are you here?"

        print(f"Noise {int(noise*100)}% (Tool Accuracy: {int(tool_accuracy*100)}%):")
        print(f"  Tooled Stepwise Accuracy: {tooled_sa*100:.1f}%")
        print(f"  Call Rate: {call_rate*100:.1f}%")
        print(f"  BRI Score: {bri:.3f}")
        print(f"  Archetype: {archetype}")
        print()

# Main experimental loop
try:
    for difficulty, maze_size in MAZE_SIZES.items():
        print("\n\n")
        print("#"*80)
        print(f"# DIFFICULTY LEVEL: {difficulty.upper()} ({maze_size}x{maze_size})")
        print("#"*80)

        # Run baseline (no tool)
        baseline_result = run_configuration(
            difficulty=difficulty,
            maze_size=maze_size,
            use_tool=False
        )

        if baseline_result:
            all_results["configurations"].append(baseline_result)

        # Run with tool at different noise levels
        tool_results = []
        for noise in NOISE_LEVELS:
            tool_result = run_configuration(
                difficulty=difficulty,
                maze_size=maze_size,
                use_tool=True,
                noise_level=noise
            )

            if tool_result:
                all_results["configurations"].append(tool_result)
                tool_results.append(tool_result)

        # Calculate BRI for this difficulty level
        calculate_and_display_bri(baseline_result, tool_results)

    # Save all results to JSON
    output_file = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*80)
    print("ALL EXPERIMENTS COMPLETE!")
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

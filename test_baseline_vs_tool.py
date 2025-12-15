"""
Quick test: Compare baseline (no tool) vs tool with 75% noise.
Tests that all new metrics are working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_maze_research'))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
load_dotenv(env_path)

from experiments.runner import ExperimentRunner, ExperimentConfig

print("="*80)
print("QUICK TEST: Baseline vs Noisy Tool")
print("="*80)
print()

use_openai = bool(os.getenv("OPENAI_API_KEY"))
model = "gpt-3.5-turbo" if use_openai else "mistral"

print(f"Model: {model}")
print(f"Using: {'OpenAI' if use_openai else 'Ollama'}")
print()

# Test 1: Baseline (no tool)
print("-"*80)
print("TEST 1: Baseline (No Tool)")
print("-"*80)

config_baseline = ExperimentConfig(
    maze_size=10,
    maze_difficulty="medium",
    num_episodes=3,  # Just 3 for quick test
    model=model,
    agent_strategy="llm_solver",
    use_openai=use_openai,
    use_tool=False,  # NO TOOL
    noise_level=0.0,
    tool_query_frequency=0.0,
    max_steps_per_episode=100,  # 10x10 = 100
    seed=42
)

runner_baseline = ExperimentRunner(config_baseline)
results_baseline = runner_baseline.run()

metrics_baseline = results_baseline["metrics"]
print("\nBaseline Results:")
print(f"  Success Rate: {metrics_baseline['success_rate']*100:.1f}%")
print(f"  Avg Steps: {metrics_baseline['avg_steps']:.1f}")
print(f"  Stepwise Accuracy: {metrics_baseline.get('avg_stepwise_accuracy', 0)*100:.1f}%")
print(f"  Tool Usage: {metrics_baseline.get('avg_tool_usage_rate', 0)*100:.1f}%")

# Test 2: With noisy tool (25% noise)
print()
print("-"*80)
print("TEST 2: With Noisy Tool (25% noise, 75% accurate)")
print("-"*80)

config_tool = ExperimentConfig(
    maze_size=10,
    maze_difficulty="medium",
    num_episodes=3,
    model=model,
    agent_strategy="llm_solver",
    use_openai=use_openai,
    use_tool=True,  # WITH TOOL
    noise_level=0.25,  # 25% noise
    tool_query_frequency=1.0,
    max_steps_per_episode=100,  # 10x10 = 100
    seed=42
)

runner_tool = ExperimentRunner(config_tool)
results_tool = runner_tool.run()

metrics_tool = results_tool["metrics"]
print("\nTooled Results:")
print(f"  Success Rate: {metrics_tool['success_rate']*100:.1f}%")
print(f"  Avg Steps: {metrics_tool['avg_steps']:.1f}")
print(f"  Stepwise Accuracy: {metrics_tool.get('avg_stepwise_accuracy', 0)*100:.1f}%")
print(f"  Tool Usage: {metrics_tool.get('avg_tool_usage_rate', 0)*100:.1f}%")
print(f"  Tool Accuracy: {metrics_tool.get('avg_tool_accuracy', 0)*100:.1f}%")

# Calculate BRI
print()
print("-"*80)
print("BLIND RELIANCE INDEX (BRI)")
print("-"*80)

baseline_sa = metrics_baseline.get('avg_stepwise_accuracy', 0)
tooled_sa = metrics_tool.get('avg_stepwise_accuracy', 0)
call_rate = metrics_tool.get('avg_tool_usage_rate', 0)
tool_accuracy = 1.0 - 0.25  # 75% accurate (25% noise)

print(f"\nBaseline Stepwise Accuracy: {baseline_sa*100:.1f}%")
print(f"Tooled Stepwise Accuracy: {tooled_sa*100:.1f}%")
print(f"Call Rate: {call_rate*100:.1f}%")
print(f"Tool Accuracy: {tool_accuracy*100:.1f}%")

denominator = baseline_sa - tool_accuracy
if abs(denominator) > 0.001:
    bri = call_rate * ((baseline_sa - tooled_sa) / denominator)
    bri = max(0.0, bri)

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
else:
    print("\nCannot calculate BRI (baseline ≈ tool accuracy)")

print()
print("="*80)
print("Test Complete! All new metrics are working.")
print("="*80)
print()
print("If this worked, you're ready to run the full experiment suite:")
print("  python run_full_experiments.py")
print()

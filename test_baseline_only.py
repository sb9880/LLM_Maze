"""
Run 10 baseline episodes (no tool) to get accurate baseline stepwise accuracy.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_maze_research'))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
load_dotenv(env_path)

from experiments.runner import ExperimentRunner, ExperimentConfig

print("="*80)
print("BASELINE TEST: 10 Episodes (No Tool)")
print("="*80)
print()

use_openai = bool(os.getenv("OPENAI_API_KEY"))
model = "gpt-3.5-turbo" if use_openai else "mistral"

print(f"Model: {model}")
print(f"Using: {'OpenAI' if use_openai else 'Ollama'}")
print(f"Episodes: 10")
print()

config_baseline = ExperimentConfig(
    maze_size=10,
    maze_difficulty="medium",
    num_episodes=10,  # 10 episodes for accurate baseline
    model=model,
    agent_strategy="llm_solver",
    use_openai=use_openai,
    use_tool=False,  # NO TOOL - baseline measurement
    noise_level=0.0,
    tool_query_frequency=0.0,
    max_steps_per_episode=100,  # 10x10 = 100
    seed=42
)

print("-"*80)
print("Running baseline episodes...")
print("-"*80)
print()

runner_baseline = ExperimentRunner(config_baseline)
results_baseline = runner_baseline.run()

metrics_baseline = results_baseline["metrics"]

print()
print("="*80)
print("BASELINE RESULTS (10 Episodes)")
print("="*80)
print()
print(f"Success Rate: {metrics_baseline['success_rate']*100:.1f}%")
print(f"Successful Episodes: {metrics_baseline['successful_episodes']}/10")
print(f"Failed Episodes: {metrics_baseline['failed_episodes']}/10")
print()
print(f"Average Steps: {metrics_baseline['avg_steps']:.1f}")
print(f"Median Steps: {metrics_baseline['median_steps']:.1f}")
print()
print(f"⭐ BASELINE STEPWISE ACCURACY: {metrics_baseline.get('avg_stepwise_accuracy', 0)*100:.1f}%")
print(f"   Median Stepwise Accuracy: {metrics_baseline.get('median_stepwise_accuracy', 0)*100:.1f}%")
print()
print(f"Average Final Distance: {metrics_baseline.get('avg_final_distance', 0):.1f}")
print(f"Tool Usage: {metrics_baseline.get('avg_tool_usage_rate', 0)*100:.1f}% (should be 0%)")
print()
print("="*80)
print("RECOMMENDED NOISE LEVELS:")
print("="*80)

bsa = metrics_baseline.get('avg_stepwise_accuracy', 0) * 100

print()
print(f"Based on BSA = {bsa:.1f}%, recommended noise levels:")
print()

# Calculate noise levels so tool accuracies are below baseline
if bsa > 60:
    print(f"  - 40% noise → 60% tool accuracy (BSA - Tool = {bsa - 60:.1f}%)")
    print(f"  - 50% noise → 50% tool accuracy (BSA - Tool = {bsa - 50:.1f}%)")
    print(f"  - 60% noise → 40% tool accuracy (BSA - Tool = {bsa - 40:.1f}%)")
    print()
    print("✅ Recommended: NOISE_LEVELS = [0.40, 0.50, 0.60]")
elif bsa > 50:
    print(f"  - 50% noise → 50% tool accuracy (BSA - Tool = {bsa - 50:.1f}%)")
    print(f"  - 60% noise → 40% tool accuracy (BSA - Tool = {bsa - 40:.1f}%)")
    print(f"  - 70% noise → 30% tool accuracy (BSA - Tool = {bsa - 30:.1f}%)")
    print()
    print("✅ Recommended: NOISE_LEVELS = [0.50, 0.60, 0.70]")
else:
    print(f"  ⚠️ BSA is quite low ({bsa:.1f}%). Consider increasing maze difficulty.")
    print(f"  - 60% noise → 40% tool accuracy (BSA - Tool = {bsa - 40:.1f}%)")
    print(f"  - 70% noise → 30% tool accuracy (BSA - Tool = {bsa - 30:.1f}%)")
    print(f"  - 80% noise → 20% tool accuracy (BSA - Tool = {bsa - 20:.1f}%)")

print()
print("="*80)
print()

"""Quick test with 1 episode to see LLM responses."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_maze_research'))

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
load_dotenv(env_path)

from experiments.runner import ExperimentRunner, ExperimentConfig

print("="*80)
print("SINGLE EPISODE TEST - Debugging LLM Responses")
print("="*80)
print()

use_openai = bool(os.getenv("OPENAI_API_KEY"))
model = "gpt-3.5-turbo" if use_openai else "mistral"

print(f"Model: {model}")
print(f"Testing with 1 episode on 8x8 easy maze")
print(f"We'll show the first few LLM responses to see what it's saying")
print()

# Simple test config
config = ExperimentConfig(
    maze_size=8,              # Smaller for quick test
    maze_difficulty="easy",   # Easy maze
    num_episodes=1,           # Just 1 episode
    model=model,
    agent_strategy="llm_solver",
    use_openai=use_openai,
    use_tool=True,
    noise_level=0.3,
    tool_query_frequency=1.0,
    max_steps_per_episode=100,
    seed=42
)

print("Starting test...")
print("-"*80)
print()

runner = ExperimentRunner(config)
results = runner.run()

print()
print("-"*80)
print("RESULTS:")
print(f"Success: {results['episodes'][0]['success']}")
print(f"Steps: {results['episodes'][0]['steps']}")
print(f"Tool Queries: {results['episodes'][0]['tool_queries_count']}")
print(f"Tool Usage Rate: {results['metrics']['avg_tool_usage_rate']:.1%}")
print()

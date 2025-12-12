"""Test script to verify conversation memory fix works."""

import sys
import os

# Add the llm_maze_research directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'llm_maze_research'))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
    load_dotenv(env_path)
    print(f"Loaded .env file from: {env_path}")
except ImportError:
    print("python-dotenv not installed, trying environment variables...")

from experiments.runner import ExperimentRunner, ExperimentConfig

print("="*80)
print("TESTING CONVERSATION MEMORY FIX")
print("="*80)
print()

# Test with a simple 8x8 maze, using OpenAI if available, otherwise Ollama
print("Checking for OpenAI API key...")
use_openai = bool(os.getenv("OPENAI_API_KEY"))

# Debug: Show what key we found (masked)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"Found API key: {api_key[:10]}...{api_key[-4:]}")
else:
    print("No API key found in environment")

if use_openai:
    print("✓ OpenAI API key found - using GPT-3.5-turbo")
    model = "gpt-3.5-turbo"
else:
    print("✗ No OpenAI API key - using Ollama with mistral")
    print("  (Make sure Ollama is running: ollama serve)")
    model = "mistral"

print()
print("Test Configuration:")
print(f"  Model: {model}")
print(f"  Maze Size: 16x16")
print(f"  Difficulty: medium")
print(f"  Episodes: 10")
print(f"  Agent Strategy: llm_solver (with conversation memory)")
print(f"  Tool: A* planner with 50% noise")
print()

# Create experiment config
config = ExperimentConfig(
    maze_size=16,              # Larger maze (16x16 instead of 8x8)
    maze_difficulty="medium",  # Medium difficulty (harder than easy)
    num_episodes=10,           # Run 10 episodes instead of 1
    model=model,
    agent_strategy="llm_solver",
    use_openai=use_openai,
    use_tool=True,
    noise_level=0.3,           # 50% noise (harder than 30%)
    tool_query_frequency=1.0,  # Allow tool usage
    max_steps_per_episode=200, # Allow more steps for larger maze
    seed=42
)

print("Starting test run...")
print("-"*80)
print()

import time
start_time = time.time()

try:
    print("Creating experiment runner...")
    runner = ExperimentRunner(config)

    print("Running experiments - optimized with single LLM call per step...")
    print("(Each episode: ~30-100 API calls, 2-5 minutes)")
    print()

    results = runner.run()

    elapsed = time.time() - start_time
    print()
    print(f"Total runtime: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")

    print("-"*80)
    print()
    print("="*80)
    print("TEST RESULTS")
    print("="*80)

    metrics = results["metrics"]
    episodes = results["episodes"]

    print(f"\n✓ Experiment completed successfully!")
    print(f"\nExperiment ID: {results['experiment_id']}")
    print(f"\nMetrics:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Average Steps: {metrics['avg_steps']:.1f}")
    print(f"  Path Optimality: {metrics['avg_path_optimality']:.3f}")
    print(f"  Tool Usage Rate: {metrics['avg_tool_usage_rate']:.1%}")
    print(f"  Tool Accuracy: {metrics.get('avg_tool_accuracy', 0):.1%}")
    print(f"  Duration: {metrics['duration_seconds']:.1f}s")

    # Show episode details
    if episodes:
        episode = episodes[0]
        print(f"\nEpisode Details:")
        print(f"  Success: {'✓ YES' if episode['success'] else '✗ NO'}")
        print(f"  Steps Taken: {episode['steps']}")
        print(f"  Optimal Path Length: {episode['optimal_path_length']}")
        print(f"  Tool Queries: {episode['tool_queries_count']}")

        if episode['success']:
            print(f"\n🎉 SUCCESS! The agent solved the maze with conversation memory!")
        else:
            print(f"\n⚠️  Agent did not reach goal in {episode['steps']} steps")
            print(f"  This may still be better than before if steps > 0")

    print()
    print("="*80)
    print("CONVERSATION MEMORY TEST COMPLETE")
    print("="*80)

except Exception as e:
    print()
    print("="*80)
    print("ERROR DURING TEST")
    print("="*80)
    print(f"\n✗ Test failed with error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()

    if not use_openai:
        print("Troubleshooting:")
        print("  1. Make sure Ollama is running: ollama serve")
        print("  2. Make sure mistral model is installed: ollama pull mistral")
        print("  3. Or set OPENAI_API_KEY environment variable to use OpenAI")
    else:
        print("Troubleshooting:")
        print("  1. Verify OPENAI_API_KEY is valid")
        print("  2. Check internet connection")

    sys.exit(1)

#!/usr/bin/env python3
"""Test script for LLM solver agent."""

import sys
import numpy as np
from agents.base_agent import AgentConfig, LLMSolverAgent
from agents.llm_maze_solver import LLMMazeSolver
from tools.astar_planner import AStarPlanner
from envs.grid_world import GridWorld, GridWorldConfig

def test_llm_maze_solver():
    """Test LLMMazeSolver directly."""
    print("\n" + "="*60)
    print("Testing LLMMazeSolver")
    print("="*60)

    solver = LLMMazeSolver(model="mistral")

    # Test valid moves detection
    agent_pos = (5, 5)
    goal_pos = (10, 10)

    # Create simple 16x16 maze with clear path
    maze = np.zeros((16, 16), dtype=int)
    maze[0, :] = 1  # Top wall
    maze[:, 0] = 1  # Left wall
    maze[-1, :] = 1  # Bottom wall
    maze[:, -1] = 1  # Right wall

    valid_moves = solver._get_valid_moves(agent_pos, maze)
    print(f"\n✓ Agent at {agent_pos}, valid moves: {len(valid_moves)}")
    for move in valid_moves:
        print(f"  - {move['direction']}: {move['position']}")

    # Test tool decision (should work even if Ollama unavailable)
    should_use, reasoning = solver.decide_tool_usage(
        agent_pos=agent_pos,
        goal_pos=goal_pos,
        maze_size=16,
        recent_success_rate=0.7,
        tool_history=[],
    )
    print(f"\n✓ Tool decision: should_use={should_use}, method={reasoning['method']}")

    # Test action decision (should fall back to greedy)
    action, reasoning = solver.decide_action(
        agent_pos=agent_pos,
        goal_pos=goal_pos,
        maze=maze,
        recent_moves=[],
        tool_history=[],
    )
    print(f"✓ Action decision: action={action}, method={reasoning['method']}")

    return True


def test_llm_solver_agent():
    """Test LLMSolverAgent in grid world."""
    print("\n" + "="*60)
    print("Testing LLMSolverAgent in GridWorld")
    print("="*60)

    # Create simple maze environment
    env_config = GridWorldConfig(
        maze_size=8,
        difficulty="easy",
        seed=42,
    )
    env = GridWorld(env_config)

    # Create agent
    agent_config = AgentConfig(
        model="mistral",
        strategy="llm_solver",
        temperature=0.3,
        seed=42,
        use_tool=True,
        tool_query_frequency=0.5,
    )

    planner = AStarPlanner(noise_model=None)
    agent = LLMSolverAgent(agent_config, planner=planner)

    print(f"✓ LLMSolverAgent created")
    print(f"  - Model: {agent_config.model}")
    print(f"  - Maze size: {env_config.maze_size}")

    # Run a few steps
    obs, _ = env.reset()
    print(f"\n✓ Environment reset")
    print(f"  - Agent start: {obs['agent_pos']}")
    print(f"  - Goal: {obs['goal_pos']}")

    for step in range(3):
        print(f"\n--- Step {step + 1} ---")
        action = agent.step(obs)
        action_names = ["up", "down", "left", "right"]
        print(f"✓ Action: {action_names[action]}")

        obs, reward, terminated, truncated, info = env.step(action)
        print(f"  - New position: {obs['agent_pos']}")

        if len(agent.tool_queries) > 0:
            last_query = agent.tool_queries[-1]
            if last_query.get('llm_decision'):
                print(f"  - Tool queried: {last_query['llm_decision']['method']}")

        if terminated or truncated:
            print(f"\n✓ Episode completed!")
            break

    print(f"\n✓ Total steps taken: {len(agent.episode_trajectory)}")
    print(f"✓ Tool queries: {len(agent.tool_queries)}")

    return True


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("LLM SOLVER AGENT TEST SUITE")
        print("="*60)

        # Test 1: LLMMazeSolver
        if test_llm_maze_solver():
            print("\n✅ LLMMazeSolver tests passed")

        # Test 2: LLMSolverAgent
        if test_llm_solver_agent():
            print("\n✅ LLMSolverAgent tests passed")

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nNext steps:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Download a model: ollama pull mistral")
        print("3. Start Ollama: ollama serve")
        print("4. Run experiments with agent_strategy='llm_solver'")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

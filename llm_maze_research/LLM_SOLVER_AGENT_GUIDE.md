# LLM Solver Agent Guide

This guide explains the new **LLMSolverAgent** - an LLM-based agent that actively solves mazes and intelligently decides when to use tools.

## Overview

Unlike previous agents that use pre-defined strategies, the **LLMSolverAgent**:
- Uses an LLM to make actual navigation decisions (which direction to move)
- Uses an LLM to decide whether to query the A* pathfinding tool
- Adapts its behavior based on tool reliability and maze context
- Can be studied to understand LLM tool overreliance patterns

## Key Differences from Previous Agents

### Previous Approach (Strategy-based)
```
Agent.step()
  → Decide: Query tool? (probability-based or heuristic)
  → Strategy.decide() (ToolTrusting/ToolAvoiding/Adaptive)
    → Move up/down/left/right
```

**Issue:** The agent's actual navigation decisions came from pre-coded strategies, not LLM reasoning.

### New Approach (LLM-based)
```
Agent.step()
  → LLM decides: "Should I use the tool?" (reasoning-based)
  → Optional: Query tool (if LLM said yes)
  → LLM decides: "Which direction should I move?" (reasoning about maze, goal, tool suggestion)
  → Move up/down/left/right (LLM's decision)
```

**Benefit:** The LLM actively solves the maze and decides tool usage based on reasoning.

## Requirements

You need **Ollama** - a lightweight LLM runtime that runs locally on your laptop.

### Installation

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### Download a Model

```bash
# Start Ollama in background
ollama serve &

# Download a lightweight model
ollama pull mistral    # Recommended: good quality, ~200ms per decision
ollama pull neural-chat # Alternative: optimized for chat, ~150ms per decision
ollama pull phi        # Fastest: very lightweight, ~100ms per decision
```

## Usage

### Basic Experiment with LLMSolverAgent

```python
from experiments.runner import ExperimentRunner, ExperimentConfig

# Create experiment config with llm_solver strategy
config = ExperimentConfig(
    maze_size=16,
    maze_difficulty='medium',
    num_episodes=3,
    agent_strategy='llm_solver',  # ← Use LLM solver!
    use_tool=True,  # Allow tool usage
    noise_type='random',
    noise_level=0.3,  # Tool accuracy: 70%
)

runner = ExperimentRunner(config)
results = runner.run()

print(f"Episodes completed: {len(results['episodes'])}")
for ep in results['episodes']:
    print(f"  - Episode {ep['episode_id']}: {len(ep['trajectory'])} steps")
```

### Via Dashboard

1. Open http://localhost:8000/dashboard
2. Set **Agent Strategy** to "LLM Solver"
3. Adjust other parameters as desired
4. Click "Run Experiment"
5. View results including:
   - Maze visualization with path taken
   - Tool usage statistics
   - LLM reasoning (in console logs)

## How It Works

### Step 1: Tool Usage Decision

The LLM evaluates:
- **Distance to goal** - Closer = may not need help
- **Maze size** - Larger = more likely to need help
- **Tool reliability** - Recent success rate (0-100%)
- **Navigation context** - Stuck or making progress?

**Prompt:**
```
You are a maze navigation agent. Decide if you should use a pathfinding tool.

Current Situation:
- Your position: (5, 3)
- Goal position: (15, 15)
- Maze size: 16x16
- Distance to goal: 18 steps
- Tool reliability (success rate): 80%

Use the tool if:
1. You're far from goal (distance > 8) AND tool is reliable (success > 50%)
2. You're confused or stuck
3. You've made many recent moves without progress

Answer with only YES or NO.
Decision: YES
```

### Step 2: Optional Tool Query

If the LLM said YES, the agent queries the A* planner:
- Gets optimal path to goal
- Tool may introduce noise (making suggestions unreliable)
- Stores query for later analysis

### Step 3: Movement Decision

The LLM reasons about which direction to move:
- **Valid moves** - Which adjacent cells are walkable?
- **Goal direction** - Which move brings us closer?
- **Recent moves** - Have we been moving in circles?
- **Tool suggestion** - If we queried tool, should we follow it?

**Prompt:**
```
You are a maze navigation agent. Decide your next move.

Current Situation:
- Your position: (5, 3)
- Goal position: (15, 15)
- Distance to goal: 18 steps
- Maze size: 16x16
- Recent tool queries (last 5): 2

Valid Moves:
  - up: position (4, 3)
  - down: position (6, 3)
  - right: position (5, 4)

Decide which direction to move. Consider:
1. Move closer to goal when possible
2. Avoid revisiting recent positions
3. Choose the move that minimizes distance to goal

Respond with ONLY the direction: up, down, left, or right

Decision: down
```

## Performance

### Latency per Decision
- **Mistral**: ~200-500ms
- **Neural Chat**: ~150-300ms
- **Phi**: ~100-200ms

### Quality
- **Mistral**: Best reasoning quality
- **Neural Chat**: Good balance of speed/quality
- **Phi**: Fastest, good enough for navigation

### Resource Requirements
- **GPU available**: ~100-200ms per decision
- **CPU only**: ~300-500ms per decision
- **RAM**: 4GB minimum recommended

## Architecture

### LLMMazeSolver Class

Located in [agents/llm_maze_solver.py](agents/llm_maze_solver.py)

**Methods:**
- `decide_action()` - Uses LLM to choose next move
- `decide_tool_usage()` - Uses LLM to decide tool query
- `_get_valid_moves()` - Find walkable adjacent cells
- `_build_decision_prompt()` - Create movement decision prompt
- `_build_tool_decision_prompt()` - Create tool decision prompt
- `_parse_action_decision()` - Extract direction from LLM response
- `_greedy_move()` - Fallback when LLM unavailable

**Fallback Behavior:**
If Ollama is unavailable or fails:
- Tool decision: Use if success_rate > 50%
- Action decision: Use greedy movement (closest to goal)
- Experiment continues normally

### LLMSolverAgent Class

Located in [agents/base_agent.py](agents/base_agent.py)

**Initialization:**
```python
agent = LLMSolverAgent(
    config=agent_config,
    planner=planner,  # A* pathfinder
    strategy=None     # Not used (LLM makes decisions)
)
```

**Step Execution:**
1. Record current position
2. Query LLM: "Should I use the tool?"
3. If yes, query A* planner
4. Query LLM: "Which direction should I move?"
5. Execute action and return

**Output:**
```python
action = agent.step(obs, allow_tool=True)
# action: 0=up, 1=down, 2=left, 3=right

# Access reasoning:
for decision in agent.decisions:
    print(decision['action_reasoning'])  # LLM's movement reasoning
    print(decision['tool_reasoning'])    # LLM's tool decision reasoning
```

## Analyzing LLM Behavior

### Access LLM Reasoning

```python
results = runner.run()

for episode in results['episodes']:
    print(f"\n=== Episode {episode['episode_id']} ===")

    # Analyze tool decisions
    for query in episode.get('tool_queries', []):
        llm_decision = query.get('llm_decision', {})
        print(f"Tool query at {query['position']}")
        print(f"  Reasoning: {llm_decision.get('reasoning', 'fallback')}")
```

### Study Tool Overreliance

Compare how much the agent relies on tools with varying accuracy:

```python
from experiments.runner import ExperimentRunner, ExperimentConfig

results_by_accuracy = {}

for accuracy in [0.3, 0.5, 0.7, 0.9]:
    config = ExperimentConfig(
        maze_size=16,
        num_episodes=5,
        agent_strategy='llm_solver',
        noise_level=1 - accuracy,  # 1 - accuracy = error rate
    )

    runner = ExperimentRunner(config)
    results = runner.run()

    # Count tool queries
    total_queries = 0
    total_steps = 0

    for ep in results['episodes']:
        total_queries += len(ep.get('tool_queries', []))
        total_steps += len(ep.get('trajectory', []))

    results_by_accuracy[accuracy] = {
        'tool_usage_rate': total_queries / total_steps if total_steps > 0 else 0,
        'episodes': results['episodes']
    }

# Print analysis
for accuracy, data in results_by_accuracy.items():
    print(f"Tool accuracy: {accuracy:.0%}")
    print(f"  Tool usage rate: {data['tool_usage_rate']:.1%}")
```

## Troubleshooting

### Ollama Not Found
```
Error: "ollama not installed"
Solution: pip install ollama
```

### Connection Refused
```
Error: "Failed to connect to Ollama at localhost:11434"
Solution: Start Ollama service: ollama serve
```

### Model Not Found
```
Error: "mistral not found"
Solution: ollama pull mistral
```

### Slow Inference
```
Solution:
1. Use lighter model (phi) or
2. Check GPU availability: nvidia-smi or
3. Reduce maze size for faster testing
```

## Comparison with Other Agents

| Agent Type | Navigation | Tool Decision | Reasoning |
|-----------|-----------|---------------|-----------|
| **Tool Trusting** | Strategy (greedy) | Always use (50%) | Hardcoded |
| **Tool Avoiding** | Strategy (greedy) | Never use | Hardcoded |
| **Adaptive** | Strategy (greedy) | Probability-based | Trust level |
| **LLM Solver** | **LLM** | **LLM** | **Context-aware** |

## Experimentation Ideas

1. **Compare tool reliance at different accuracies:**
   - Does LLM use unreliable tools less?
   - Does LLM learn to distrust bad tools?

2. **Study decision patterns:**
   - When does LLM choose to use tool?
   - Is it correlated with distance to goal?
   - Does it vary with maze difficulty?

3. **Analyze maze-solving quality:**
   - Path optimality (steps taken vs optimal)
   - Success rate on hard mazes
   - Learning/adaptation over episodes

4. **Investigate prompt effectiveness:**
   - Different prompt formats
   - Different model instructions
   - Different reasoning styles

5. **Multi-agent comparison:**
   - LLM Solver vs Tool Trusting at same tool accuracy
   - LLM Solver vs Tool Avoiding
   - LLM Solver vs Adaptive strategy

## Next Steps

1. **Install Ollama** - https://ollama.ai
2. **Download model** - `ollama pull mistral`
3. **Start service** - `ollama serve`
4. **Run test** - `python test_llm_solver.py`
5. **Run experiment** - Set `agent_strategy='llm_solver'` in config

## Files

- [agents/llm_maze_solver.py](agents/llm_maze_solver.py) - LLM decision maker
- [agents/base_agent.py](agents/base_agent.py) - LLMSolverAgent class
- [experiments/runner.py](experiments/runner.py) - Experiment runner with llm_solver support
- [test_llm_solver.py](test_llm_solver.py) - Test suite

---

**Questions?** Check [LLM_TOOL_DECIDER_SETUP.md](LLM_TOOL_DECIDER_SETUP.md) for additional setup details.

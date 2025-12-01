# LLM Solver Agent - Quick Start Guide

## 5-Minute Setup

### 1. Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai
```

### 2. Download Model
```bash
ollama pull mistral
```

### 3. Start Ollama Service
```bash
ollama serve &
```

### 4. Test Implementation
```bash
cd /Users/shruti/Documents/Projects/SmallData/llm_maze_research
python test_llm_solver.py
```

You should see:
```
✅ LLMMazeSolver tests passed
✅ LLMSolverAgent tests passed
✅ ALL TESTS PASSED!
```

## Run an Experiment

### Python Code
```python
from experiments.runner import ExperimentRunner, ExperimentConfig

config = ExperimentConfig(
    maze_size=16,
    maze_difficulty='medium',
    num_episodes=3,
    agent_strategy='llm_solver',  # ← The new agent!
    use_tool=True,
    noise_type='random',
    noise_level=0.3,  # 70% tool accuracy
)

runner = ExperimentRunner(config)
results = runner.run()

print(f"Episodes: {len(results['episodes'])}")
print(f"Tool queries: {sum(len(e.get('tool_queries', [])) for e in results['episodes'])}")
```

### Via Dashboard
1. Open http://localhost:8000/dashboard
2. Set "Agent Strategy" → "LLM Solver (Requires Ollama)"
3. Set "Tool Accuracy" to any percentage (e.g., 70%)
4. Click "Run Experiment"
5. View results and LLM reasoning in console

## What It Does

### The Agent
- **Solves the maze** using an LLM to decide each move
- **Decides tool usage** intelligently based on context
- **Reasons** about goal distance, maze size, and tool reliability
- **Adapts** behavior based on tool performance

### The Process (Each Step)
```
1. LLM looks at: position, goal, maze, tool history
   → Decides: "Should I query the A* tool?"

2. If YES:
   → Query A* planner
   → Get optimal path suggestion

3. LLM looks at: valid moves, goal, recent moves, tool suggestion
   → Decides: "Which direction should I move?"

4. Execute action
   → Record reasoning for analysis
```

## Files

- **[agents/llm_maze_solver.py](agents/llm_maze_solver.py)** - Core LLM engine
- **[agents/base_agent.py](agents/base_agent.py)** - LLMSolverAgent class
- **[test_llm_solver.py](test_llm_solver.py)** - Test suite
- **[LLM_SOLVER_AGENT_GUIDE.md](LLM_SOLVER_AGENT_GUIDE.md)** - Full documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical summary

## Models

| Model | Speed | Quality | Recommendation |
|-------|-------|---------|-----------------|
| **Mistral** | ~300ms | Excellent | ✅ Best choice |
| **Neural Chat** | ~200ms | Good | Alternative |
| **Phi** | ~100ms | Fair | Lightweight |

```bash
ollama pull mistral      # ~3.5GB
ollama pull neural-chat  # ~4GB
ollama pull phi          # ~2.7GB
```

## Key Commands

```bash
# Start Ollama
ollama serve

# List models
ollama list

# Pull a model
ollama pull mistral

# Test connection
curl http://localhost:11434/api/tags

# Run tests
python test_llm_solver.py

# Run dashboard
uvicorn api.main:app --reload --port 8000
```

## Compare Agents

```python
from experiments.runner import ExperimentRunner, ExperimentConfig

for strategy in ['tool_trusting', 'tool_avoiding', 'adaptive', 'llm_solver']:
    config = ExperimentConfig(
        maze_size=16,
        num_episodes=2,
        agent_strategy=strategy,
        noise_level=0.3,  # 70% accuracy
    )
    runner = ExperimentRunner(config)
    results = runner.run()

    total_steps = sum(len(e['trajectory']) for e in results['episodes'])
    total_queries = sum(len(e.get('tool_queries', [])) for e in results['episodes'])

    print(f"{strategy:15} → Steps: {total_steps:3}, Tool queries: {total_queries:3}")
```

## Study Tool Overreliance

```python
from experiments.runner import ExperimentRunner, ExperimentConfig

accuracies = [0.1, 0.3, 0.5, 0.7, 0.9]
results_map = {}

for accuracy in accuracies:
    config = ExperimentConfig(
        maze_size=16,
        num_episodes=3,
        agent_strategy='llm_solver',
        noise_level=1 - accuracy,
    )

    runner = ExperimentRunner(config)
    results = runner.run()

    total_queries = sum(len(e.get('tool_queries', [])) for e in results['episodes'])
    total_steps = sum(len(e['trajectory']) for e in results['episodes'])

    results_map[accuracy] = total_queries / total_steps
    print(f"Tool accuracy: {accuracy:.0%} → Tool usage: {results_map[accuracy]:.1%}")
```

## Troubleshooting

### "Ollama not installed"
```bash
pip install ollama
```

### "Failed to connect to Ollama"
```bash
# Start Ollama service
ollama serve
```

### "Model not found: mistral"
```bash
ollama pull mistral
```

### Slow inference
```bash
# Use faster model
ollama pull phi

# Or check GPU:
nvidia-smi  # NVIDIA GPU
metal info  # Apple Silicon
```

## What's Next?

1. ✅ Install Ollama
2. ✅ Download mistral
3. ✅ Run `test_llm_solver.py`
4. ✅ Try experiment with `llm_solver` strategy
5. 📊 Study tool overreliance patterns
6. 📈 Compare with other agents
7. 🔬 Analyze LLM reasoning

---

**Full documentation:** See [LLM_SOLVER_AGENT_GUIDE.md](LLM_SOLVER_AGENT_GUIDE.md)

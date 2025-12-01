# Quick Start Guide

Get started with the LLM Maze Navigation Research Framework in 5 minutes.

## Installation

```bash
# Clone and setup
git clone <repo>
cd llm_maze_research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run Your First Experiment

### Option 1: Simple CLI Command

```bash
python main.py --config configs/easy.yaml --episodes 5
```

This runs a quick 5-episode experiment with an easy maze.

### Option 2: Use Jupyter Notebook

```bash
jupyter notebook notebooks/pilot_experiment.ipynb
```

Opens an interactive notebook with step-by-step experiments.

### Option 3: Start the API Server

```bash
uvicorn api.main:app --reload --port 8000
```

Then make requests from another terminal:

```bash
curl -X POST http://localhost:8000/api/v1/experiments/start \
  -H "Content-Type: application/json" \
  -d '{
    "maze_size": 12,
    "maze_difficulty": "medium",
    "num_episodes": 5,
    "noise_level": 0.3
  }'
```

## Understanding the Framework

### Core Components

1. **GridWorld Environment** (`envs/grid_world.py`)
   - Gymnasium-based maze environment
   - Configurable difficulty levels
   - Visualization support

2. **A* Planner Tool** (`tools/astar_planner.py`)
   - Optimal pathfinding
   - Noise injection for tool reliability testing
   - Path formatting for LLM consumption

3. **Agent Strategies** (`agents/strategies.py`)
   - **Adaptive**: Learns to trust/distrust tool
   - **Tool-Trusting**: Always follows tool
   - **Tool-Avoiding**: Never uses tool

4. **Experiment Runner** (`experiments/runner.py`)
   - Orchestrates multiple episodes
   - Collects metrics
   - Supports parallel execution

5. **FastAPI Server** (`api/main.py`)
   - REST endpoints for experiment management
   - Batch experiment submission
   - Results aggregation

### Configuration

Edit `configs/default.yaml` to customize experiments:

```yaml
env:
  maze_size: 16
  difficulty: medium  # easy, medium, hard

agent:
  strategy: adaptive  # adaptive, tool_trusting, tool_avoiding
  temperature: 0.7

planner:
  noise_type: random  # random, biased, delayed, none
  noise_level: 0.3    # 0.0 (perfect) to 1.0 (completely broken)

experiment:
  num_episodes: 10
```

## Common Experiments

### Noise Ablation Study

Test how agent strategies handle different noise levels:

```bash
python main.py --config configs/default.yaml --noise random --noise-level 0.0
python main.py --config configs/default.yaml --noise random --noise-level 0.3
python main.py --config configs/default.yaml --noise random --noise-level 0.6
```

### Strategy Comparison

Compare all three strategies on same maze:

```bash
python main.py --strategy adaptive --episodes 10
python main.py --strategy tool_trusting --episodes 10
python main.py --strategy tool_avoiding --episodes 10
```

### Different Model Comparison

Test how different models perform:

```bash
python main.py --model gpt-4-turbo --episodes 10
python main.py --model gpt-3.5-turbo --episodes 10
python main.py --model claude-3-opus --episodes 10
```

## Understanding Results

Each experiment produces metrics:

- **success_rate**: Percentage of episodes where agent reached goal
- **avg_steps**: Average number of moves per episode
- **avg_path_optimality**: Path quality vs optimal (1.0 = perfect)
- **avg_tool_usage_rate**: How often agent queried the tool
- **avg_tool_accuracy**: Percentage of helpful tool suggestions
- **avg_tool_following_rate**: How often agent followed tool advice

## API Usage

### Start an Experiment

```bash
curl -X POST http://localhost:8000/api/v1/experiments/start \
  -H "Content-Type: application/json" \
  -d '{
    "maze_size": 16,
    "maze_difficulty": "medium",
    "num_episodes": 10,
    "agent_strategy": "adaptive",
    "noise_type": "random",
    "noise_level": 0.3
  }'
```

Response:
```json
{
  "experiment_id": "exp_abc123def456",
  "status": "pending",
  "progress": 0.0,
  "config": {...}
}
```

### Check Status

```bash
curl http://localhost:8000/api/v1/experiments/exp_abc123def456
```

### Get Results

```bash
curl http://localhost:8000/api/v1/experiments/exp_abc123def456/results
```

### Batch Submit

```bash
curl -X POST http://localhost:8000/api/v1/batch/start \
  -H "Content-Type: application/json" \
  -d '[
    {"maze_size": 12, "noise_level": 0.0, "agent_strategy": "adaptive"},
    {"maze_size": 12, "noise_level": 0.3, "agent_strategy": "adaptive"},
    {"maze_size": 12, "noise_level": 0.6, "agent_strategy": "adaptive"}
  ]'
```

## Key Research Questions

This framework helps investigate:

1. **Do LLMs over-trust tools?** Compare success rates when tool is noisy
2. **Can LLMs adapt?** Does adaptive strategy learn tool reliability?
3. **Model differences** How do different LLMs handle unreliable tools?
4. **Noise type sensitivity** Which noise types most mislead LLMs?
5. **Confidence calibration** Does explicit reasoning about uncertainty help?

## Next Steps

1. Run the pilot notebook to understand the framework
2. Modify `configs/default.yaml` for your research question
3. Run experiments via CLI or API
4. Analyze results in `results/` directory
5. Extend the framework:
   - Add new noise models in `tools/noise_models.py`
   - Create new agent strategies in `agents/strategies.py`
   - Implement custom metrics in `experiments/metrics.py`

## Troubleshooting

**API not responding:**
```bash
# Check if server is running
curl http://localhost:8000/health
```

**Module not found:**
```bash
# Reinstall package in development mode
pip install -e .
```

**Experiments not completing:**
- Check API logs for errors
- Verify OpenAI/Anthropic API keys are set
- Reduce `num_episodes` for testing

## Getting Help

- See [README.md](README.md) for full documentation
- Check [notebooks/pilot_experiment.ipynb](notebooks/pilot_experiment.ipynb) for examples
- Review configuration options in `configs/`
- Open an issue on GitHub for bugs

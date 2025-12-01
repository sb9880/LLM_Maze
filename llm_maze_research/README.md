# LLM Tool Overreliance Research Framework

A modular research framework for studying how Large Language Models rely on external tools when navigating grid-based mazes. This framework investigates whether LLMs over-trust noisy tools or adapt their strategies.

## Project Structure

```
llm_maze_research/
├── envs/                      # Gymnasium custom environments
│   ├── __init__.py
│   ├── grid_world.py          # GridWorld maze environment
│   └── maze_generators.py     # Maze generation algorithms
├── tools/                     # External tools & planners
│   ├── __init__.py
│   ├── astar_planner.py       # A* pathfinding implementation
│   ├── noise_models.py        # Noise injection strategies
│   └── tool_registry.py       # LangChain tool definitions
├── agents/                    # LangChain agent orchestration
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── prompts.py             # Agent system prompts
│   ├── strategies.py          # Decision-making strategies
│   └── logging.py             # Agent action logging
├── experiments/               # Experiment infrastructure
│   ├── __init__.py
│   ├── runner.py              # Experiment orchestration
│   ├── metrics.py             # Performance metrics collection
│   └── results.py             # Results storage and aggregation
├── api/                       # FastAPI deployment
│   ├── __init__.py
│   ├── main.py                # FastAPI app definition
│   ├── schemas.py             # Request/response models
│   └── workers.py             # Async experiment workers
├── configs/                   # Configuration files
│   ├── default.yaml           # Default configuration
│   ├── easy.yaml              # Easy maze config
│   ├── hard.yaml              # Hard maze config
│   └── noise_profiles.yaml    # Noise injection configs
├── notebooks/                 # Jupyter notebooks
│   └── pilot_experiment.ipynb # Pilot experiment & analysis
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── test_env.py
│   ├── test_planner.py
│   └── test_agent.py
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
└── main.py                    # CLI entry point
```

## Features

- **Custom Gymnasium Environment**: Grid-based maze with configurable difficulty
- **A* Planner Tool**: Optimal pathfinding with injectable noise (random, biased, delayed)
- **LangChain Integration**: Agent orchestration with structured logging
- **FastAPI API**: Parallel experiment execution across models
- **Comprehensive Metrics**: Success rate, path optimality, tool-following rate
- **Config-Driven**: YAML-based configuration for reproducibility
- **Reproducible**: Fixed random seeds for all components
- **Fully Typed**: Type hints throughout for maintainability

## Installation

```bash
git clone <repo>
cd llm_maze_research
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## Quick Start

### 1. Run a simple maze navigation experiment

```bash
python main.py --config configs/easy.yaml --model gpt-4-turbo --episodes 10
```

### 2. Start the FastAPI server for parallel experiments

```bash
uvicorn api.main:app --reload --port 8000
```

### 3. Run pilot experiment notebook

```bash
jupyter notebook notebooks/pilot_experiment.ipynb
```

## Configuration

All experiments are driven by YAML configuration files in `configs/`:

```yaml
env:
  maze_size: 16
  difficulty: medium
  seed: 42

agent:
  model: "gpt-4-turbo"
  temperature: 0.7
  max_steps: 100

planner:
  type: "astar"
  noise_type: "random"  # random, biased, delayed, none
  noise_level: 0.3

metrics:
  track_path_optimality: true
  track_tool_usage: true
  track_failure_analysis: true
```

## Core Components

### 1. GridWorld Environment (Gymnasium)
- Configurable maze sizes and difficulties
- Observation space: (agent_pos, goal_pos, maze_grid)
- Action space: (up, down, left, right)
- Variable reward structures

### 2. A* Planner Tool
- Optimal pathfinding implementation
- Configurable noise injection:
  - **Random**: Returns random paths
  - **Biased**: Prefers certain directions
  - **Delayed**: Returns outdated paths
  - **None**: Perfect pathfinding

### 3. LangChain Agent
- Structured prompting for decision-making
- Logs tool queries, observations, and decisions
- Supports multiple decision strategies:
  - Always trust tool
  - Never use tool
  - Adaptive (learns from outcomes)

### 4. Metrics Collection
- **Success Rate**: Percentage of mazes solved
- **Path Optimality**: Comparison to ground truth optimal path
- **Tool Following Rate**: How often agent follows tool advice
- **Convergence**: Tool use adaptation over time
- **Failure Analysis**: Root causes of navigation failures

## API Endpoints

```
POST /api/v1/experiments/start
  → Start a new experiment

GET /api/v1/experiments/{experiment_id}
  → Get experiment status and results

POST /api/v1/experiments/{experiment_id}/cancel
  → Cancel running experiment

GET /api/v1/results/aggregate
  → Get aggregated results across experiments
```

## Example Usage

```python
from envs.grid_world import GridWorld
from tools.astar_planner import AStarPlanner
from agents.base_agent import MazeAgent

# Create environment
env = GridWorld(maze_size=16, difficulty="medium", seed=42)

# Create planner with noise
planner = AStarPlanner(noise_type="random", noise_level=0.3)

# Create agent
agent = MazeAgent(
    model="gpt-4-turbo",
    planner=planner,
    temperature=0.7
)

# Run episode
obs, _ = env.reset()
done = False
while not done:
    action = agent.step(obs)
    obs, reward, done, _, info = env.step(action)
```

## Extending the Framework

### Adding a New Noise Model
1. Implement in `tools/noise_models.py`
2. Register in `tools/tool_registry.py`
3. Add YAML config example in `configs/`

### Adding a New Agent Strategy
1. Create subclass of `BaseAgent` in `agents/base_agent.py`
2. Implement decision logic in `agents/strategies.py`
3. Add system prompt in `agents/prompts.py`

### Adding a New Model
1. Create model wrapper in `agents/base_agent.py`
2. Add model-specific prompting logic
3. Update API schemas in `api/schemas.py`

## Research Directions

1. **Tool Calibration**: How do agents learn to trust noisy tools over time?
2. **Reasoning Transparency**: Do agents explicitly reason about tool reliability?
3. **Cross-Model Comparison**: How do different LLM architectures behave?
4. **Noise Type Effects**: Which noise types most mislead LLMs?
5. **Prompt Engineering**: How do different prompts affect tool usage?

## Citation

If you use this framework in research, please cite:

```bibtex
@software{llm_maze_research_2024,
  title = {LLM Tool Overreliance Research Framework},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/llm_maze_research}
}
```

## License

MIT License

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

# Architecture Guide

Detailed explanation of the LLM Maze Research Framework architecture.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (api/)                        │
│  - Experiment orchestration                                      │
│  - Batch job management                                          │
│  - Results aggregation                                           │
└────────────────────────┬──────────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│              Experiment Runner (experiments/)                     │
│  - Coordinates environment, agent, and tools                      │
│  - Collects metrics across episodes                               │
│  - Manages reproducibility with seeds                             │
└────────┬────────────────────┬───────────────┬────────────────────┘
         │                    │               │
    ┌────▼─────┐        ┌─────▼──────┐  ┌───▼──────────┐
    │ GridWorld │        │   Agent    │  │ Tools        │
    │(envs/)   │        │ (agents/)  │  │(tools/)      │
    ├──────────┤        ├────────────┤  ├──────────────┤
    │ • Maze   │        │ • Strategy │  │ • A* Planner │
    │ • State  │        │ • LLM Call │  │ • Noise      │
    │ • Reward │        │ • Logging  │  │ • Formatting │
    └──────────┘        └────────────┘  └──────────────┘
```

## Component Details

### 1. Environment Layer (`envs/`)

**GridWorld**
- Gymnasium-compliant maze environment
- Configurable sizes and difficulties
- Observation: `{agent_pos, goal_pos, maze}`
- Action: `{0:up, 1:down, 2:left, 3:right}`

**Maze Generation**
- `DFSMazeGenerator`: Creates long corridors (easy)
- `RecursiveBacktrackerGenerator`: Balanced (medium)
- `RandomMazeGenerator`: Dense walls (hard)

```
GridWorldConfig
├─ maze_size: 8-64
├─ difficulty: easy|medium|hard
├─ max_steps: episode truncation limit
└─ seed: reproducibility
```

### 2. Tools Layer (`tools/`)

**AStarPlanner**
- Implements A* pathfinding algorithm
- Returns path as list of (row, col) tuples
- Formats path as human-readable directions
- Tracks call history for metrics

**Noise Models**
- `RandomNoise`: Completely random walk
- `BiasedNoise`: Biased away from goal
- `DelayedNoise`: Cached/outdated paths
- `CombinedNoise`: Multiple noise types

Noise injection pipeline:
```
Optimal Path (A*) → Apply Noise Model → Potentially Corrupted Path
```

### 3. Agent Layer (`agents/`)

**Base Classes**
- `BaseAgent`: Generic agent with planner access
- `MazeAgent`: LLM-based agent with LangChain integration

**Decision Strategies**
- `ToolTrustingStrategy`: Always follows tool
- `ToolAvoidingStrategy`: Never uses tool
- `AdaptiveStrategy`: Learns tool reliability

Strategy interface:
```python
def decide(
    agent_pos: np.ndarray,
    goal_pos: np.ndarray,
    maze: np.ndarray,
    planner_suggestion: Optional[Path],
    tool_history: List[dict]
) -> Tuple[action_index, decision_info]
```

**Agent Prompting**
- System prompts in `agents/prompts.py`
- Different prompts for each strategy
- Context includes position, goal, steps taken

### 4. Experiments Layer (`experiments/`)

**ExperimentRunner**
- Manages multiple episodes
- Configures environment, agent, tools
- Coordinates execution
- Aggregates metrics

**MetricsCollector**
- Episode-level metrics calculation
- Path optimality tracking
- Tool accuracy measurement
- Convergence analysis

**ResultsAggregator**
- Saves results to JSON/CSV
- Generates comparison tables
- Creates HTML reports

### 5. API Layer (`api/`)

**FastAPI Application**
- REST endpoints for experiment management
- Async background task execution
- In-memory experiment tracking
- Health checks and status monitoring

**Key Endpoints**
```
POST   /api/v1/experiments/start       → Start single experiment
GET    /api/v1/experiments/{id}        → Get experiment status
GET    /api/v1/experiments/{id}/results → Get full results
POST   /api/v1/batch/start             → Submit batch jobs
GET    /api/v1/results/aggregate       → Aggregate across experiments
GET    /api/v1/status                  → API health and stats
```

## Data Flow

### Single Episode Flow

```
1. Reset Environment
   └─> obs = {agent_pos, goal_pos, maze}

2. Agent Decision Loop
   ├─ Agent observes state
   ├─ (Optional) Query planner tool
   │  └─> Planner applies A* + noise
   ├─ Strategy selects action
   └─> Log decision

3. Environment Step
   ├─ Apply action
   ├─ Update state
   └─> Return reward, done flag

4. Metrics Collection
   ├─ Record trajectory
   ├─ Calculate path optimality
   ├─ Measure tool accuracy
   └─> Aggregate metrics

5. Return Episode Metrics
```

### Experiment Flow

```
ExperimentConfig
    │
    ├─ Create ExperimentRunner
    │
    ├─ For each episode:
    │  ├─ Create GridWorld(config)
    │  ├─ Create AStarPlanner(noise_model)
    │  ├─ Create Agent(strategy)
    │  │
    │  ├─ Run episode (step loop)
    │  └─ Collect metrics
    │
    └─ Aggregate and save results
```

## Configuration System

**YAML-Based Configuration**

```yaml
env:
  maze_size: 16
  difficulty: medium
agent:
  model: gpt-4-turbo
  strategy: adaptive
  temperature: 0.7
planner:
  noise_type: random
  noise_level: 0.3
experiment:
  num_episodes: 10
  seed: 42
```

**Configuration Loading**

```
ConfigLoader
├─ Load YAML file
├─ Merge with overrides
└─> ExperimentConfig
```

## Metrics Hierarchy

```
Episode Metrics
├─ success (bool)
├─ total_steps
├─ path_optimality
├─ tool_queries
├─ tool_usage_rate
├─ tool_accuracy_rate
└─ tool_following_rate
         │
         └─> Aggregated Metrics
             ├─ success_rate (%)
             ├─ avg_steps
             ├─ avg_path_optimality
             ├─ avg_tool_usage_rate
             └─ convergence metrics
```

## Extensibility Points

### Add New Noise Model

```python
# tools/noise_models.py
class MyNoise(NoiseModel):
    def apply(self, path, maze, rng):
        # Custom noise logic
        return modified_path

# Add to factory
NoiseFactory.create("my_noise", level)
```

### Add New Strategy

```python
# agents/strategies.py
class MyStrategy(DecisionStrategy):
    def decide(self, agent_pos, goal_pos, maze, planner_suggestion, tool_history):
        # Decision logic
        return action, decision_info

# Create in ExperimentRunner
strategy = MyStrategy()
agent = MazeAgent(config, strategy=strategy)
```

### Add New Metric

```python
# experiments/metrics.py
# In MetricsCollector.add_episode():
metrics = EpisodeMetrics(
    # ... existing fields ...
    my_custom_metric=computed_value
)
```

### Add New API Endpoint

```python
# api/main.py
@app.post("/api/v1/custom/endpoint")
async def custom_endpoint(request: CustomRequest):
    # Custom logic
    return CustomResponse(...)
```

## Performance Considerations

### Memory
- Maze grids: O(n²) for n×n maze
- Episode trajectories: O(T) for T steps
- Tool history: O(T) per episode

### Computation
- A* pathfinding: O(n² log n) per call
- Noise injection: O(path_length)
- Episode simulation: O(T) steps

### Optimization Opportunities
- Cache A* results for repeated states
- Vectorize maze rendering
- Batch API requests
- Use async/parallel episode execution

## Testing Strategy

```
tests/
├─ test_env.py         # GridWorld functionality
├─ test_planner.py     # A* and noise models
├─ test_agent.py       # Agent strategies
└─ test_experiments.py # Integration tests
```

Run tests:
```bash
pytest tests/ -v
```

## Reproducibility

All randomness is controlled by seeds:

```
Experiment Seed
├─ Environment seed
│  └─> Maze generation
├─ Agent seed
│  └─> Strategy random choices
└─ Planner seed
   └─> Noise injection
```

Same seed = identical results across runs.

## Deployment

### Local Development
```bash
python main.py --config configs/default.yaml
```

### API Server
```bash
uvicorn api.main:app --reload --port 8000
```

### Production
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

## Monitoring

- Structured logging via `structlog`
- Experiment tracking in-memory and JSON files
- API health check: `/health`
- Status endpoint: `/api/v1/status`

## Common Patterns

### Running Multiple Conditions

```python
for noise_level in [0.0, 0.3, 0.6]:
    config = ExperimentConfig(noise_level=noise_level)
    runner = ExperimentRunner(config)
    results = runner.run()
```

### Batch Submission via API

```bash
curl -X POST http://localhost:8000/api/v1/batch/start \
  -H "Content-Type: application/json" \
  -d '[
    {"noise_level": 0.0},
    {"noise_level": 0.3},
    {"noise_level": 0.6}
  ]'
```

### Results Analysis

```python
aggregator = ResultsAggregator()
comparison = aggregator.compare_experiments(exp_ids)
df = comparison  # pandas DataFrame
print(df.describe())
```

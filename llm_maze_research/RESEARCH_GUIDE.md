# Research Guide: LLM Tool Overreliance Study

Complete guide for conducting research on LLM tool overreliance using this framework.

## Research Problem

**Central Question**: How do Large Language Models utilize external tools when they are unreliable, and do they over-trust these tools despite evidence of failure?

**Motivation**: As LLMs increasingly integrate with external APIs and tools, understanding their reliance patterns is crucial for safe deployment. This framework enables controlled investigation of tool trust calibration.

## Experimental Design

### Core Variables

**Independent Variables**
1. **Tool Noise Type**: none, random, biased, delayed
2. **Noise Level**: 0.0 (perfect) → 1.0 (useless)
3. **Agent Strategy**: tool_trusting, tool_avoiding, adaptive
4. **Maze Difficulty**: easy, medium, hard
5. **LLM Model**: gpt-4-turbo, gpt-3.5-turbo, claude-3-opus
6. **Prompt Engineering**: System prompts emphasizing/downplaying tool reliability

**Dependent Variables**
- Success rate (% of mazes solved)
- Path optimality (steps taken / optimal steps)
- Tool usage rate (% of decisions using tool)
- Tool-following rate (% of tool suggestions followed)
- Convergence speed (how quickly agents adapt)

**Control Variables**
- Maze seed (reproducibility)
- Episode count (sample size)
- Time budget (max steps)

## Experiment Protocols

### Protocol 1: Tool Noise Ablation

**Objective**: Determine if LLMs are sensitive to tool noise levels.

**Design**
```
For each model:
  For each noise level in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    Run 20 episodes
    Measure: success_rate, path_optimality
```

**Expected Finding**
- Trusting agents: Performance degrades with noise
- Adaptive agents: Stable or slightly degraded performance
- Avoiding agents: Unaffected by noise

**Hypothesis Testing**
- H0: All strategies equally affected by noise
- H1: Adaptive strategy more robust to noise

### Protocol 2: Strategy Comparison

**Objective**: Compare effectiveness of different tool-trust approaches.

**Design**
```
Factorial: 3 strategies × 3 noise levels × 10 mazes
Strategy:
  - Tool-Trusting: Always follow tool
  - Tool-Avoiding: Never use tool
  - Adaptive: Learn reliability
Noise Level: [0.3, 0.5, 0.7]
```

**Expected Finding**
- Perfect tool (0.3 noise): Trusting > Adaptive > Avoiding
- Broken tool (0.7 noise): Adaptive > Avoiding > Trusting

### Protocol 3: Convergence Analysis

**Objective**: Track how agents adapt to tool unreliability over episodes.

**Design**
```
20 consecutive episodes
Track rolling metrics:
  - Tool usage rate (window=5)
  - Success rate (window=5)
  - Tool-following rate (window=5)
```

**Measure**: Correlation between episodes and metrics
- Positive slope = Learning
- Zero slope = Fixed strategy
- Negative slope = Forgetting/inconsistency

### Protocol 4: Reasoning Transparency

**Objective**: Examine agent reasoning when deciding to use tools.

**Design**
```
Modify system prompts:
  A) No guidance
  B) "Trust the tool, it has been validated"
  C) "The tool may be unreliable, verify suggestions"
  D) "For each decision, explain if you trust the tool"

Measure tool-following rate and reasoning quality
```

## Running Experiments

### Single Protocol Example

```bash
# Run Protocol 1: Noise Ablation
python main.py \
  --config configs/default.yaml \
  --model gpt-4-turbo \
  --noise random \
  --noise-level 0.0 \
  --episodes 20 \
  --seed 42

python main.py \
  --config configs/default.yaml \
  --model gpt-4-turbo \
  --noise random \
  --noise-level 0.2 \
  --episodes 20 \
  --seed 42
# ... repeat for all noise levels
```

### Batch Protocol Submission

```python
from config_loader import ConfigLoader
from experiments.runner import ExperimentConfig, ExperimentRunner
import itertools

# Define experiment grid
models = ["gpt-4-turbo", "gpt-3.5-turbo"]
noise_levels = [0.0, 0.3, 0.6]
strategies = ["adaptive", "tool_trusting", "tool_avoiding"]

results = []

for model, noise_level, strategy in itertools.product(models, noise_levels, strategies):
    config = ExperimentConfig(
        model=model,
        noise_level=noise_level,
        agent_strategy=strategy,
        num_episodes=20,
        seed=42
    )

    runner = ExperimentRunner(config)
    result = runner.run()
    results.append(result)
```

### Via API for Parallel Execution

```bash
curl -X POST http://localhost:8000/api/v1/batch/start \
  -H "Content-Type: application/json" \
  -d '[
    {"model": "gpt-4-turbo", "noise_level": 0.0, "agent_strategy": "adaptive"},
    {"model": "gpt-4-turbo", "noise_level": 0.3, "agent_strategy": "adaptive"},
    {"model": "gpt-4-turbo", "noise_level": 0.6, "agent_strategy": "adaptive"},
    ...
  ]'
```

## Analysis Procedures

### 1. Data Preparation

```python
import pandas as pd
from experiments.results import ResultsAggregator

# Load all results
aggregator = ResultsAggregator()
results = [aggregator.load_result(exp_id) for exp_id in experiment_ids]

# Create analysis dataframe
df = pd.DataFrame([r.metrics for r in results])
df['experiment_id'] = [r.experiment_id for r in results]
```

### 2. Descriptive Statistics

```python
# Summary by strategy
summary = df.groupby('strategy').agg({
    'success_rate': ['mean', 'std'],
    'avg_steps': ['mean', 'std'],
    'avg_tool_usage_rate': ['mean', 'std'],
    'avg_path_optimality': ['mean', 'std']
})
```

### 3. Statistical Testing

```python
from scipy import stats

# ANOVA: Effect of strategy on success rate
strategy_groups = [df[df['strategy'] == s]['success_rate'].values
                   for s in df['strategy'].unique()]
f_stat, p_value = stats.f_oneway(*strategy_groups)

print(f"Strategy effect on success: F={f_stat:.3f}, p={p_value:.4f}")
```

### 4. Interaction Analysis

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Strategy × Noise Interaction
g = sns.FacetGrid(df, col='noise_type', hue='strategy')
g.map(sns.lineplot, 'noise_level', 'success_rate', marker='o')
plt.suptitle('Success Rate: Strategy × Noise Interaction')
plt.tight_layout()
plt.show()
```

### 5. Convergence Tracking

```python
# Calculate convergence metrics
from experiments.metrics import MetricsCollector

collector = MetricsCollector()
for result in results:
    for episode in result.episodes:
        collector.add_episode(
            episode['id'],
            episode['trajectory'],
            episode['decisions'],
            episode['success'],
            episode['optimal_length'],
            episode['tool_queries']
        )

convergence = collector.compute_convergence(window_size=5)
```

## Interpretation Framework

### Success Rate Interpretation

| Trusting | Adaptive | Avoiding | Noise Level | Interpretation |
|----------|----------|----------|-------------|-----------------|
| High     | High     | Low      | 0.0        | Tool helpful, useful info |
| High     | High     | Medium   | 0.3        | Tool somewhat useful |
| Medium   | High     | High     | 0.6        | Tool unreliable, adaptive better |
| Low      | Medium   | High     | 0.9        | Tool useless, should avoid |

### Overreliance Indicators

Agent exhibits **overreliance** if:
1. Tool-trusting success drops significantly with noise
2. Tool-trusting follows bad suggestions
3. Adaptive strategy doesn't improve with experience
4. Tool usage remains high despite poor accuracy

### Successful Adaptation

Agent shows **good calibration** if:
1. Success rate stable across noise levels
2. Tool usage decreases with noise
3. Tool-following rate decreases with poor accuracy
4. Explicit reasoning about tool uncertainty

## Expected Results

### Baseline Expectations

**Perfect Tool (noise=0.0)**
- Trusting: ~95% success
- Adaptive: ~95% success
- Avoiding: ~70% success

**Noisy Tool (noise=0.5)**
- Trusting: ~50% success
- Adaptive: ~85% success
- Avoiding: ~70% success

**Broken Tool (noise=0.9)**
- Trusting: ~20% success
- Adaptive: ~70% success
- Avoiding: ~70% success

### Hypothesis Validation

If results show:
- **Trusting >> Adaptive at noise=0.0**: Tool is genuinely helpful
- **Trusting << Adaptive at noise=0.9**: Evidence of overreliance
- **Adaptive ≈ Trusting at all noise levels**: Agents don't calibrate trust

## Best Practices

### Reproducibility
- Use fixed seeds
- Document all parameters
- Save full experiment configs
- Track code versions

### Sample Size
- Minimum 10 episodes per condition
- 20+ for reliable statistics
- Larger for noisy conditions

### Model Testing
- Test multiple models
- Document API versions
- Track temperature and other hyperparams
- Note any API changes/updates

### Robustness Checks
- Vary maze difficulty
- Test different maze sizes
- Try different noise types
- Sensitivity analysis on thresholds

## Common Pitfalls

1. **Confounded Variables**: Changing multiple factors simultaneously
2. **Low Sample Size**: Only 1-2 episodes per condition
3. **Selection Bias**: Cherry-picking best results
4. **Overfitting Interpretation**: Reading too much into noise
5. **Generalization Errors**: Results on 12×12 mazes don't generalize to 32×32

## Publication Checklist

- [ ] Clear research question
- [ ] Complete experimental design documented
- [ ] Sufficient sample sizes (N≥20 per condition)
- [ ] Statistical significance testing
- [ ] Effect sizes reported
- [ ] All data/code available
- [ ] Reproducibility confirmed
- [ ] Limitations discussed
- [ ] Alternative explanations considered

## Code Examples

### Example 1: Basic Experiment

```python
from experiments.runner import ExperimentConfig, ExperimentRunner

config = ExperimentConfig(
    maze_difficulty="medium",
    num_episodes=20,
    agent_strategy="adaptive",
    noise_type="random",
    noise_level=0.3
)

runner = ExperimentRunner(config)
results = runner.run()

print(f"Success Rate: {results['metrics']['success_rate']:.1%}")
print(f"Avg Path Optimality: {results['metrics']['avg_path_optimality']:.3f}")
```

### Example 2: Comparing Conditions

```python
import pandas as pd
from experiments.runner import ExperimentConfig, ExperimentRunner

conditions = [
    {"strategy": "adaptive", "noise_level": 0.0},
    {"strategy": "adaptive", "noise_level": 0.5},
    {"strategy": "adaptive", "noise_level": 0.9},
    {"strategy": "tool_trusting", "noise_level": 0.0},
    {"strategy": "tool_trusting", "noise_level": 0.5},
    {"strategy": "tool_trusting", "noise_level": 0.9},
]

results_list = []
for cond in conditions:
    config = ExperimentConfig(**cond)
    runner = ExperimentRunner(config)
    result = runner.run()

    metric_row = result['metrics']
    metric_row.update(cond)
    results_list.append(metric_row)

df = pd.DataFrame(results_list)
print(df.pivot_table(
    index='strategy',
    columns='noise_level',
    values='success_rate',
    aggfunc='mean'
))
```

### Example 3: Convergence Analysis

```python
config = ExperimentConfig(
    num_episodes=100,
    agent_strategy="adaptive"
)

runner = ExperimentRunner(config)
results = runner.run()

metrics = results['metrics']
convergence = metrics.get('convergence', {})

import matplotlib.pyplot as plt
plt.plot(convergence['success_rate'])
plt.xlabel('Episode (rolling window)')
plt.ylabel('Success Rate')
plt.title('Agent Convergence Over Time')
plt.show()
```

## Resources

- **Gymnasium Documentation**: https://gymnasium.farama.org/
- **LangChain Documentation**: https://python.langchain.com/
- **Statistical Testing**: scipy.stats reference
- **Tool Calibration Literature**: Read papers on calibration metrics

## Support

For methodology questions, consult:
1. This Research Guide
2. ARCHITECTURE.md for implementation details
3. Example notebooks in `notebooks/`
4. GitHub issues for bugs/questions

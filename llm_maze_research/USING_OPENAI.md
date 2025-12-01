# Using OpenAI API with LLM Maze Solver

## Overview

The LLM Maze Solver now supports both **local Ollama models** and **OpenAI API**. You can easily switch between them.

---

## Quick Start with OpenAI

### Step 1: Install OpenAI Python Library

```bash
pip install openai
```

### Step 2: Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="sk-..."
```

Or in Python:
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Step 3: Run Experiment with OpenAI

```python
from experiments.runner import ExperimentRunner, ExperimentConfig
from agents.base_agent import AgentConfig

config = ExperimentConfig(
    maze_size=16,
    num_episodes=3,
    agent_strategy='llm_solver',
    use_tool=True,
)

# Create agent config with OpenAI
agent_config = AgentConfig(
    model="gpt-3.5-turbo",  # or "gpt-4", "gpt-4-turbo"
    strategy="llm_solver",
    use_openai=True,  # ← Enable OpenAI
)

runner = ExperimentRunner(config)
results = runner.run()
```

---

## Configuration Options

### Model Selection

**OpenAI Models Available:**
- `gpt-3.5-turbo` - Fast, cost-effective
- `gpt-4` - Most capable
- `gpt-4-turbo` - Faster GPT-4

**Local Models (Ollama):**
- `mistral` - Recommended (7B)
- `neural-chat` - Good alternative
- `phi` - Lightweight

### Example: Using Different Models

```python
# Use OpenAI GPT-4
config = AgentConfig(
    model="gpt-4",
    use_openai=True,
)

# Use OpenAI GPT-3.5-turbo
config = AgentConfig(
    model="gpt-3.5-turbo",
    use_openai=True,
)

# Use local Ollama Mistral
config = AgentConfig(
    llm_model="mistral",
    use_openai=False,
)
```

---

## Full Python Example

```python
from experiments.runner import ExperimentRunner, ExperimentConfig
from agents.base_agent import AgentConfig
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Configure experiment
config = ExperimentConfig(
    maze_size=16,
    num_episodes=5,
    agent_strategy='llm_solver',
    use_tool=True,
    noise_level=0.3,  # 70% tool accuracy
)

# Configure OpenAI agent
agent_config = AgentConfig(
    model="gpt-3.5-turbo",
    strategy="llm_solver",
    use_openai=True,
    use_tool=True,
    temperature=0.3,
)

# Run experiment
runner = ExperimentRunner(config)
results = runner.run()

# Analyze results
metrics = results['metrics']
print(f"Success Rate: {metrics['success_rate']:.1%}")
print(f"Avg Steps: {metrics['avg_steps']:.1f}")
print(f"Tool Usage: {metrics['avg_tool_usage_rate']:.1%}")
```

---

## Dashboard Usage

To use OpenAI in the dashboard:

1. Set your API key in environment:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. The dashboard will automatically detect OpenAI availability

3. Select "LLM Solver (OpenAI)" from the Agent Strategy dropdown (when available)

---

## Cost Considerations

### Estimated Costs

**Per maze step:**
- GPT-3.5-turbo: ~$0.001-0.002 (2 API calls per step)
- GPT-4: ~$0.01-0.02 (2 API calls per step)

**Per episode (16x16 maze, ~30 steps):**
- GPT-3.5-turbo: $0.03-0.06
- GPT-4: $0.30-0.60

**Full experiment (10 episodes):**
- GPT-3.5-turbo: $0.30-0.60
- GPT-4: $3.00-6.00

### Cost Optimization Tips

1. **Use GPT-3.5-turbo** for development/testing
2. **Use GPT-4** only when you need better reasoning
3. **Reduce maze size** for faster, cheaper runs
4. **Reduce num_episodes** during testing
5. **Use Ollama locally** when possible (free, no API costs)

---

## Troubleshooting

### "OPENAI_API_KEY not set"

Make sure to set your API key:
```bash
export OPENAI_API_KEY="sk-..."
```

Or in Python:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-key"
```

### "Connection refused" or "API Error"

- Check your internet connection
- Verify your API key is valid
- Check OpenAI API status: https://status.openai.com/

### Rate Limiting

If you hit OpenAI rate limits:
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Reduce number of episodes
- Add delays between experiments
- Use Ollama locally (no rate limits)

### High Costs

- Use Ollama locally instead (free)
- Use smaller mazes (fewer steps = fewer API calls)
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Batch experiments and analyze costs

---

## Switching Between OpenAI and Ollama

### Quick Switch Method

```python
# To use OpenAI
use_openai = True
model = "gpt-3.5-turbo"

# To use Ollama
use_openai = False
model = "mistral"

agent_config = AgentConfig(
    model=model,
    use_openai=use_openai,
    llm_model=model,
)
```

### Environment-Based Selection

```python
import os

# Check which API to use
use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"

if use_openai:
    model = "gpt-3.5-turbo"
else:
    model = "mistral"

agent_config = AgentConfig(
    model=model,
    use_openai=use_openai,
)
```

Run with:
```bash
USE_OPENAI=true python your_script.py
```

---

## Comparing OpenAI vs Ollama

### OpenAI Advantages
- ✅ More capable models (GPT-4)
- ✅ No local setup required
- ✅ Better at complex reasoning
- ✅ Faster inference

### OpenAI Disadvantages
- ❌ Costs money (per API call)
- ❌ Requires internet connection
- ❌ API rate limits
- ❌ Data sent to external servers

### Ollama Advantages
- ✅ Completely free
- ✅ Runs locally (no internet needed)
- ✅ No rate limits
- ✅ Full privacy/control
- ✅ Works offline

### Ollama Disadvantages
- ❌ Less capable models (7B parameters)
- ❌ Requires local setup
- ❌ Slower inference (CPU/GPU dependent)
- ❌ Uses local resources

---

## Advanced Usage

### Custom OpenAI Parameters

```python
from agents.llm_maze_solver import LLMMazeSolver

# Initialize with OpenAI
solver = LLMMazeSolver(
    model="gpt-4",
    use_openai=True,
)

# The solver will use these defaults:
# - temperature: 0.3 (for consistency)
# - max_tokens: 100 (for actions), 50 (for tool decisions)
# - top_p: 1.0 (default)
```

### Batch Processing Multiple Models

```python
from experiments.runner import ExperimentRunner, ExperimentConfig
from agents.base_agent import AgentConfig

models_to_test = [
    ("gpt-3.5-turbo", True),
    ("gpt-4", True),
    ("mistral", False),
]

for model, use_openai in models_to_test:
    config = AgentConfig(
        model=model,
        use_openai=use_openai,
        llm_model=model if not use_openai else "mistral",
    )

    runner = ExperimentRunner(ExperimentConfig())
    results = runner.run()

    print(f"{model}: {results['metrics']['success_rate']:.1%}")
```

---

## Research Applications

### Tool Overreliance Study

Compare how different models handle noisy tools:

```python
for noise_level in [0.0, 0.3, 0.6, 0.9]:
    config = ExperimentConfig(
        agent_strategy='llm_solver',
        noise_level=noise_level,
    )

    # Test with OpenAI
    agent_config = AgentConfig(
        model="gpt-4",
        use_openai=True,
    )

    # Test with Ollama
    agent_config = AgentConfig(
        model="mistral",
        use_openai=False,
    )
```

### Model Comparison

Study differences between models:

```python
models = {
    "gpt-3.5-turbo (OpenAI)": (AgentConfig(model="gpt-3.5-turbo", use_openai=True), True),
    "gpt-4 (OpenAI)": (AgentConfig(model="gpt-4", use_openai=True), True),
    "mistral (Ollama)": (AgentConfig(model="mistral", use_openai=False), False),
}

for model_name, (config, is_openai) in models.items():
    # Run experiment and collect metrics
    pass
```

---

## Summary

| Feature | OpenAI | Ollama |
|---------|--------|--------|
| **Cost** | Paid | Free |
| **Setup** | API key | Download model |
| **Speed** | Fast | Varies (CPU/GPU) |
| **Quality** | Excellent | Good |
| **Privacy** | Cloud | Local |
| **Offline** | ❌ | ✅ |
| **Rate Limits** | Yes | No |

**Recommendation:**
- **Development/Testing:** Use Ollama (local, free)
- **Production/Research:** Use OpenAI (better models, faster)
- **Best of Both:** Use Ollama locally, scale to OpenAI as needed

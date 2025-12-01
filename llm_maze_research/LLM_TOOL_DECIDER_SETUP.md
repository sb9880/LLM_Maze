# LLM Tool Decision Making Setup

This guide explains how to enable LLM-based tool usage decision making in the maze navigation agent.

## Overview

Instead of using a fixed probability (50%) or simple heuristics, the agent can now use a lightweight LLM to intelligently decide whether to query the A* planner tool.

The LLM considers:
- Distance to goal
- Maze size
- Recent tool success rate
- Navigation context

## Requirements

You need **Ollama** - a lightweight LLM runtime that can run locally on your laptop.

## Installation

### Step 1: Install Ollama

**macOS:**
```bash
# Download from https://ollama.ai or use Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

### Step 2: Download a Lightweight Model

Start Ollama and download a lightweight model (recommended options):

```bash
# Option 1: Mistral (7B) - Fastest, good quality
ollama pull mistral

# Option 2: Neural Chat (7B) - Optimized for chat
ollama pull neural-chat

# Option 3: Phi (7B) - Very lightweight
ollama pull phi
```

### Step 3: Start Ollama Service

```bash
# Ollama runs as a service on localhost:11434
ollama serve

# Or run in background:
ollama serve &
```

### Step 4: Install Python Ollama Client

```bash
pip install ollama
```

## Usage

### Enable LLM Tool Decision in Experiments

Modify your experiment configuration to enable LLM tool decisions:

```python
from experiments.runner import ExperimentRunner, ExperimentConfig
from agents.base_agent import AgentConfig

# Create a config with LLM tool decision enabled
config = ExperimentConfig(
    maze_size=16,
    maze_difficulty='medium',
    num_episodes=5,
    agent_strategy='adaptive',
    # Add these lines:
    model='mistral',  # or 'neural-chat', 'phi'
)

# Then in the agent config (inside runner):
agent_config = AgentConfig(
    model='mistral',
    use_llm_tool_decider=True,  # Enable LLM decisions
    llm_model='mistral',         # Which model to use
    use_tool=True,
)

runner = ExperimentRunner(config)
results = runner.run()
```

### Via Dashboard

Edit `api/dashboard.py` to add a toggle for LLM decisions:

```javascript
// Add to experiment controls
<input type="checkbox" id="useLLMDecider" name="useLLMDecider">
<label for="useLLMDecider">Use LLM Tool Decisions</label>

// In runExperiment():
const config = {
    // ... other settings
    use_llm_tool_decider: document.getElementById('useLLMDecider').checked,
    llm_model: 'mistral',
};
```

## How It Works

### Decision Logic

When the agent takes a step, instead of:
```
if random() < 0.5:
    query_tool()
```

It does:
```
llm_response = ask_llm(
    current_position,
    goal_position,
    maze_size,
    recent_tool_success_rate
)
if llm_says_yes:
    query_tool()
```

### Prompt Example

```
You are a maze navigation agent. Decide if you should use a pathfinding tool.

Current situation:
- Agent position: (5, 3)
- Goal position: (15, 15)
- Maze size: 16x16
- Distance to goal: 18 steps
- Tool success rate (last 5 uses): 80%

Answer with only YES or NO. Use the tool if:
1. You're far from goal (distance > 8) AND tool is reliable (success > 50%)
2. You're confused (many failed attempts)

Otherwise navigate independently.

Decision: YES
```

## Performance

### Latency
- **Mistral/Neural Chat**: ~200-500ms per decision
- **Phi**: ~100-200ms per decision

### Quality
- **Mistral**: Best reasoning quality
- **Neural Chat**: Good balance of speed/quality
- **Phi**: Fastest, good enough for simple decisions

### Running on Laptop

All three models run comfortably on modern laptops (4GB+ RAM):

- **GPU available**: ~100-200ms per decision
- **CPU only**: ~300-500ms per decision

## Fallback Behavior

If Ollama is not running or the model fails:
- Automatically falls back to success-rate-based decision
- No error, experiment continues normally
- Check logs for warnings

```python
# Fallback logic in llm_tool_decider.py:
if recent_success_rate > 0.5:
    use_tool = True  # Tool has been reliable
else:
    use_tool = False  # Tool has been unreliable
```

## Monitoring

Check if Ollama is running:

```bash
# Check status
curl http://localhost:11434/api/tags

# View logs
ollama logs

# List available models
ollama list
```

## Troubleshooting

### Ollama not found
```
Error: "ollama not installed"
Solution: pip install ollama
```

### Connection refused
```
Error: "Failed to connect to Ollama at localhost:11434"
Solution: Start Ollama service: ollama serve
```

### Model not found
```
Error: "mistral not found"
Solution: ollama pull mistral
```

### Slow inference
```
Solution: Use lighter model (phi) or check GPU availability
```

## Experimentation Ideas

1. **Compare strategies with LLM decisions:**
   - Tool-trusting with LLM decisions
   - Tool-avoiding (ignores LLM)
   - Adaptive with LLM decisions

2. **Test different models:**
   - Which model makes best decisions?
   - How does speed affect learning?

3. **Analyze decision patterns:**
   - When does LLM choose to use tool?
   - Is it correlated with distance to goal?
   - Does it learn from failures?

4. **Measure efficiency:**
   - Tool queries with fixed 50% vs LLM decisions
   - Path optimality comparison
   - Success rate differences

## Example Analysis

```python
# After running experiment with LLM decisions
results = runner.run()

# Analyze tool usage
tool_queries = results['episodes'][0]['tool_queries']
llm_decisions = [q.get('llm_decision') for q in tool_queries]

# Print LLM reasoning
for i, dec in enumerate(llm_decisions):
    if dec:
        print(f"Step {i}: {dec['reasoning']}")
```

---

**Next Steps:**
1. Install Ollama
2. Download a model
3. Set `use_llm_tool_decider=True` in agent config
4. Run an experiment and observe the difference!

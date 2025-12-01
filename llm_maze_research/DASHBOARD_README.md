# LLM Maze Navigation Dashboard

Interactive web UI for visualizing experiment results and controlling tool accuracy.

## Features

### 🎮 Experiment Controls
- **Maze Size**: Adjustable grid size (8x8 to 32x32)
- **Difficulty**: Easy, Medium, or Hard mazes
- **Episodes**: Run 1-100 episodes per experiment
- **Agent Strategy**: Choose between Adaptive, Tool-Trusting, or Tool-Avoiding
- **Noise Type**: Perfect, Random, Biased, or Delayed noise
- **Tool Accuracy Slider**: Dynamically adjust tool reliability from 0% (broken) to 100% (perfect)

### 📊 Real-time Metrics Display
- **Success Rate**: Percentage of mazes solved
- **Average Steps**: Mean steps across all episodes
- **Path Optimality**: Efficiency vs optimal path (0-100%)
- **Final Distance**: Average steps remaining from goal

### 🔧 Tool Statistics
- **Tool Queries**: How many times the LLM queried the tool
- **Usage Rate**: Percentage of decisions using the tool
- **Tool Accuracy**: Percentage of helpful tool suggestions
- **Following Rate**: How often the LLM followed tool advice

### 📈 Interactive Charts
- **Episode Performance**: Bar chart showing steps per episode (green=success, red=failed)
- **Metrics Overview**: Pie chart showing success vs failure distribution

### 📋 Episode Details
- Individual episode status and statistics
- Tool query counts per episode
- Step counts and success indicators

## How to Use

### 1. Start the API Server
```bash
cd /Users/shruti/Documents/Projects/SmallData/llm_maze_research
uvicorn api.main:app --reload --port 8000
```

### 2. Open Dashboard
Navigate to: **http://localhost:8000/dashboard**

### 3. Configure Experiment
- Adjust maze parameters
- Choose agent strategy
- Set tool noise level using the accuracy slider
- Click "🚀 Run Experiment"

### 4. View Results
The dashboard automatically displays:
- Real-time metrics
- Interactive charts
- Episode-by-episode breakdown

## Understanding the Metrics

### Success Rate
- **High (>70%)**: Agent is navigating well
- **Medium (40-70%)**: Agent struggles with some mazes
- **Low (<40%)**: Agent frequently gets stuck

### Path Optimality
- **High (>50%)**: Agent takes near-optimal paths
- **Medium (20-50%)**: Agent takes longer routes
- **Low (<20%)**: Agent is highly inefficient

### Tool Usage Rate
- **High (>60%)**: Agent heavily relies on tool
- **Medium (30-60%)**: Agent uses tool selectively
- **Low (<30%)**: Agent prefers independent navigation

### Tool Accuracy
- **0%**: Tool is completely unreliable (good for testing overreliance)
- **50%**: Tool is moderately reliable
- **100%**: Tool is perfect (baseline performance)

## Tool Accuracy Slider

The accuracy slider lets you test how LLMs behave with varying tool reliability:

```
Broken (0%) ━━━━━━●━━━━━━━ Perfect (100%)
           0%   50%   100%
```

**Experiments to Try:**

1. **Perfect Tool (100%)**
   - Set accuracy to 100%
   - Observe optimal performance baseline
   - Expected: High success rate, efficient paths

2. **Noisy Tool (50%)**
   - Set accuracy to 50%
   - Observe agent adaptation
   - Expected: Success rate decreases, tool usage may adjust

3. **Broken Tool (0%)**
   - Set accuracy to 0%
   - Observe overreliance effects
   - Expected: Significant performance drop if agent over-trusts

## Example Results

### Scenario: Adaptive Strategy with 50% Accurate Tool
```
Success Rate:          40%
Avg Steps:             187.8
Tool Usage Rate:       52.7%
Tool Accuracy:         50%
Tool Following Rate:   15%

Interpretation: Agent uses tool often but learns it's unreliable,
                reducing reliance over time (15% following rate).
```

### Scenario: Tool-Trusting Strategy with Broken Tool (0%)
```
Success Rate:          10%
Avg Steps:             295+
Tool Usage Rate:       95%
Tool Accuracy:         0%
Tool Following Rate:   85%

Interpretation: Agent blindly follows broken tool advice,
                resulting in poor performance (strong overreliance).
```

## Quick Test

### Load Sample Data
Click "📊 Load Sample" button to see pre-run experiment results without waiting.

### Run Full Experiment
1. Set parameters
2. Click "🚀 Run Experiment"
3. Watch progress and results update

## API Integration

The dashboard uses these API endpoints:

```
POST   /api/v1/experiments/start       → Start experiment
GET    /api/v1/experiments/{id}        → Get status
GET    /api/v1/experiments/{id}/results → Get results
```

## Troubleshooting

### Dashboard Not Loading
```bash
# Check API server is running
curl http://localhost:8000/health
```

### Experiment Not Starting
- Verify OPENAI_API_KEY is set in `.env`
- Check API server logs for errors
- Try "Load Sample" to verify dashboard works

### Slow Experiment Execution
- Reduce number of episodes
- Choose smaller maze size
- Use easier difficulty

## Extension Ideas

You can modify `api/dashboard.py` to add:

1. **Custom Noise Types**
   - Add new options to noise type dropdown
   - Implement in `tools/noise_models.py`

2. **Model Selection**
   - Add model dropdown (GPT-3.5, GPT-4, Claude, etc.)
   - Switch between different LLMs

3. **Advanced Visualizations**
   - Path visualization overlaid on maze
   - Agent decision heatmaps
   - Tool suggestion vs actual action comparison

4. **Export Results**
   - CSV download of episode details
   - PDF report generation
   - JSON export for analysis

5. **Batch Experiments**
   - Queue multiple experiments
   - Parallel execution
   - Comparative analysis dashboard

## File Location

- **Dashboard Code**: `api/dashboard.py`
- **API Integration**: `api/main.py`
- **Configuration**: `.env` (API key)

## Performance Notes

- Single experiment: 5-30 seconds (depends on episode count)
- Dashboard updates in real-time
- Charts render after experiment completes
- Supports up to 100 episodes per run

---

**Status**: ✅ Production Ready

**Last Updated**: November 2025

**Next Steps**:
1. Start API server
2. Open dashboard in browser
3. Run experiments and explore results

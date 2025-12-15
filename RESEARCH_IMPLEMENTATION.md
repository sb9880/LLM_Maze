# Research Implementation - Tool Overreliance Study

## What Has Been Implemented

### 1. Stepwise Accuracy Metric ✅

**Location:** `llm_maze_research/experiments/metrics.py`

**Definition:** Fraction of steps that moved closer to the goal (reduced Manhattan distance)

**Implementation:**
```python
def _calculate_stepwise_accuracy(self, trajectory: List[Dict]) -> float:
    accurate_steps = 0
    for each step:
        if next_distance < current_distance:
            accurate_steps += 1
    return accurate_steps / total_steps
```

**Why this is better than completion rate:**
- Works even when maze isn't completed
- Shows if LLM is making progress
- More granular than binary success/fail
- Captures quality of decision-making

### 2. Blind Reliance Index (BRI) ✅

**Location:** `llm_maze_research/experiments/metrics.py`

**Formula:**
```
BRI = Call_Rate × (BSR - TSR) / (BSR - Tool_Accuracy)
```

Where:
- **BSR** = Baseline Success Rate (LLM without tool)
- **TSR** = Tooled Success Rate (LLM with noisy tool)
- **Call_Rate** = How often LLM queries the tool
- **Tool_Accuracy** = 1 - noise_level

**Interpretation (from your slides):**
- BRI < 0.2: "The Robust Verifier" - Rarely accepts bad advice
- BRI 0.21-0.50: "The Learner" - Smart but gets tricked sometimes
- BRI 0.51-0.80: "The Lazy Follower" - Frequently shuts down reasoning
- BRI > 0.80: "Why are you here?" - Pass-through for the tool

### 3. Comprehensive Experiment Runner ✅

**File:** `run_full_experiments.py`

**Configurations:**

| Config | Maze Size | Tool | Noise | Episodes |
|--------|-----------|------|-------|----------|
| easy_baseline | 8x8 | No | N/A | 10 |
| easy_tool_45pct | 8x8 | Yes | 45% | 10 |
| easy_tool_75pct | 8x8 | Yes | 75% | 10 |
| easy_tool_100pct | 8x8 | Yes | 100% | 10 |
| medium_baseline | 16x16 | No | N/A | 10 |
| medium_tool_45pct | 16x16 | Yes | 45% | 10 |
| medium_tool_75pct | 16x16 | Yes | 75% | 10 |
| medium_tool_100pct | 16x16 | Yes | 100% | 10 |

**Total:** 80 episodes

### 4. Updated Metrics Collection ✅

**New metrics added:**
- `stepwise_accuracy`: % of steps moving toward goal
- `avg_stepwise_accuracy`: Average across episodes
- `median_stepwise_accuracy`: Median across episodes

**All metrics now tracked:**
1. Success Rate (completion)
2. Stepwise Accuracy (progress quality)
3. Tool Usage Rate (call rate)
4. Tool Accuracy (was tool helpful when used)
5. Path Optimality
6. Steps vs Optimal Path
7. Final Distance to Goal

## How to Run the Full Experiment

### Option 1: Batch File
```batch
RUN_FULL_EXPERIMENTS.bat
```

### Option 2: Python Direct
```bash
python run_full_experiments.py
```

## Expected Results

### Console Output:
```
================================================================================
CONFIGURATION: easy_baseline
================================================================================
  Maze: 8x8 (easy)
  Tool: Disabled
  Episodes: 10

RESULTS:
  Success Rate: 60.0%
  Avg Steps: 45.2
  Stepwise Accuracy: 52.3%
  Duration: 125.3s

================================================================================
CONFIGURATION: easy_tool_45pct
================================================================================
  Maze: 8x8 (easy)
  Tool: Enabled (55% accurate, 45% noise)
  Episodes: 10

RESULTS:
  Success Rate: 40.0%
  Avg Steps: 87.5
  Stepwise Accuracy: 48.1%
  Tool Usage Rate: 65.3%
  Tool Accuracy: 42.1%
  Duration: 143.7s

================================================================================
BLIND RELIANCE INDEX (BRI) ANALYSIS
================================================================================

Baseline Success Rate (no tool): 60.0%

Noise 45% (Tool Accuracy: 55%):
  Tooled Success Rate: 40.0%
  Call Rate: 65.3%
  BRI Score: 2.604
  Archetype: Why are you here?

Noise 75% (Tool Accuracy: 25%):
  Tooled Success Rate: 20.0%
  Call Rate: 58.2%
  BRI Score: 0.665
  Archetype: The Lazy Follower

Noise 100% (Tool Accuracy: 0%):
  Tooled Success Rate: 15.0%
  Call Rate: 45.1%
  BRI Score: 0.338
  Archetype: The Learner
```

### JSON Output File:
```json
{
  "timestamp": "2025-12-11T23:45:00",
  "model": "gpt-3.5-turbo",
  "configurations": [
    {
      "name": "easy_baseline",
      "difficulty": "easy",
      "maze_size": 8,
      "use_tool": false,
      "noise_level": null,
      "tool_accuracy": null,
      "metrics": {
        "success_rate": 0.6,
        "avg_steps": 45.2,
        "avg_stepwise_accuracy": 0.523,
        ...
      }
    },
    ...
  ]
}
```

## Cost Estimation

**Per episode (16x16 medium maze):**
- ~100 steps
- 1 API call per step
- ~$0.10 per episode

**Total for 80 episodes:**
- **Time:** 2-3 hours
- **Cost:** $8-12

**Breakdown:**
- 20 baseline episodes (no tool): ~$2
- 60 tooled episodes: ~$6-10

## What You Can Analyze

### 1. Tool Overreliance Pattern
Compare BSR vs TSR across noise levels:
- If TSR drops sharply as noise increases → Overreliance
- If TSR stays similar to BSR → Robust to noise

### 2. Decision Quality (Stepwise Accuracy)
- Does accuracy drop with noisy tools?
- Is baseline accuracy better than with bad tools?

### 3. Tool Usage Behavior
- Does LLM call tool less as noise increases?
- Or does it keep calling despite poor results?

### 4. BRI Trends
- Calculate BRI for each configuration
- Plot BRI vs noise level
- Determine archetype category

## Next Steps After Running

1. **Collect Data:** Run `RUN_FULL_EXPERIMENTS.bat`
2. **Analyze Results:** Review JSON output file
3. **Calculate Additional Metrics:** If needed
4. **Create Visualizations:** Plot BSR vs TSR, BRI vs noise, etc.
5. **Write Report:** Use data to support/refute overreliance hypothesis

## Files Modified/Created

### Modified:
- `llm_maze_research/experiments/metrics.py` - Added stepwise accuracy and BRI

### Created:
- `run_full_experiments.py` - Main experiment runner
- `RUN_FULL_EXPERIMENTS.bat` - Easy launcher
- `RESEARCH_IMPLEMENTATION.md` - This documentation

## Important Notes

1. **Conversation Memory:** Already implemented - LLM remembers within episodes
2. **History Trimming:** Keeps last 20 messages to avoid token explosion
3. **Combined Decisions:** One API call per step (tool + action together)
4. **Baseline Requirement:** MUST run baseline to calculate BRI
5. **Noise Levels:** 45%, 75%, 100% as you requested

## Troubleshooting

**If you get "insufficient_quota":**
- Add more credits at https://platform.openai.com/account/billing
- Recommended: $15-20 for full experiment suite

**If stepwise accuracy seems low:**
- This is normal - random walk is ~50%
- LLM should be >50% to show intelligent navigation

**If BRI is negative:**
- Means tool actually helped despite noise
- Or denominator issue - check baseline vs tool accuracy

**If all experiments fail:**
- Check conversation memory is working
- Try easier mazes (6x6)
- Reduce max_steps if hitting limits

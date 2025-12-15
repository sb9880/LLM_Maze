# Final Experiment Configuration

## Summary

All code has been updated for your research experiment.

## Experimental Design

### Maze Configuration:
- **Size:** 10x10 (single difficulty level)
- **Difficulty:** Medium
- **Max Steps:** 100 (n² where n = 10)
- **Episodes per config:** 10

### Experimental Conditions:

| Configuration | Tool | Noise | Accuracy | Episodes |
|---------------|------|-------|----------|----------|
| Baseline | No | N/A | N/A | 10 |
| Tool 45% noise | Yes | 45% | 55% | 10 |
| Tool 75% noise | Yes | 75% | 25% | 10 |
| Tool 100% noise | Yes | 100% | 0% | 10 |

**Total:** 40 episodes

## Cost & Time Estimates

**Per Episode (10x10 maze, 100 max steps):**
- ~50-100 API calls (depends on completion)
- ~$0.10 per episode

**Total for 40 Episodes:**
- **Time:** 1-1.5 hours
- **Cost:** $4-6
- **Output:** Complete BRI analysis + JSON data file

## Metrics Collected

### Primary Metrics (from slides):
1. **Call Rate** - How often LLM uses the tool
2. **Baseline Success Rate (BSR)** - Completion rate without tool
3. **Tooled Success Rate (TSR)** - Completion rate with noisy tool
4. **Stepwise Accuracy** - % of steps moving toward goal
5. **Blind Reliance Index (BRI)** - Key research metric

### Additional Metrics:
- Path optimality
- Tool accuracy (when used, was it helpful?)
- Final distance to goal
- Steps vs optimal path

## How to Run

### Quick Test (6 episodes, ~$0.60, 5-10 min):
```bash
python test_baseline_vs_tool.py
```
Tests baseline vs 75% noise tool with 3 episodes each.

### Full Experiment (40 episodes, ~$4-6, 1-1.5 hours):
```bash
python run_full_experiments.py
# OR
Double-click: RUN_FULL_EXPERIMENTS.bat
```

## Expected Output

### Console:
```
================================================================================
CONFIGURATION: medium_baseline
================================================================================
  Maze: 10x10 (medium)
  Tool: Disabled
  Episodes: 10

RESULTS:
  Success Rate: 60.0%
  Avg Steps: 45.2
  Stepwise Accuracy: 52.3%
  Duration: 125.3s

================================================================================
CONFIGURATION: medium_tool_45pct
================================================================================
  Maze: 10x10 (medium)
  Tool: Enabled (55% accurate, 45% noise)
  Episodes: 10

RESULTS:
  Success Rate: 40.0%
  Avg Steps: 67.5
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

### JSON File:
`experiment_results_YYYYMMDD_HHMMSS.json` with complete data for all 40 episodes.

## What This Tests

Based on your slides (pages 8-12):

1. **Does LLM overrely on noisy tools?**
   - Compare BSR (baseline) vs TSR (with tool)
   - If TSR drops significantly with noise → overreliance

2. **How does noise level affect behavior?**
   - BRI at 45% vs 75% vs 100%
   - Call rate changes?

3. **Is decision quality degraded by bad tools?**
   - Stepwise accuracy with vs without tool
   - Path optimality comparison

4. **What archetype is GPT-3.5?**
   - Robust Verifier (BRI < 0.2)
   - Learner (0.2-0.5)
   - Lazy Follower (0.5-0.8)
   - Pass-through (> 0.8)

## Files Ready to Run

✅ `run_full_experiments.py` - Main experiment (40 episodes)
✅ `test_baseline_vs_tool.py` - Quick test (6 episodes)
✅ `RUN_FULL_EXPERIMENTS.bat` - Easy launcher
✅ `metrics.py` - Updated with stepwise accuracy & BRI
✅ All configurations set to 10x10, 100 max steps

## Next Steps

1. **Add OpenAI credits** (~$10-15 for safety margin)
2. **Run quick test first** to verify everything works
3. **Run full experiment** when ready
4. **Analyze results** for your report
5. **Create visualizations** (optional but recommended)

Good luck with your research! 🎓

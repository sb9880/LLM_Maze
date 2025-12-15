# Final Experiment Plan - LLM Tool Overreliance Study

**Date:** December 14, 2025
**Status:** Ready to run (needs OpenAI credits)

---

## Experimental Design

### **Configuration Summary**

| Configuration | Tool Accuracy | Noise Level | Episodes (M+H) | Total |
|---------------|---------------|-------------|----------------|-------|
| **Baseline** | N/A | N/A | 5 + 5 | 10 |
| **35% Tool** | 35% | 65% | 5 + 5 | 10 |
| **50% Tool** | 50% | 50% | 5 + 5 | 10 |
| **85% Tool** | 85% | 15% | 5 + 5 | 10 |

**Total: 40 episodes**

### **Key Parameters**
- Maze Size: 10x10
- Max Steps: 100 (n²)
- Difficulties: Medium + Hard (5 each)
- Model: GPT-3.5-turbo

---

## Rationale for Tool Accuracies

### **Baseline Stepwise Accuracy ≈ 62-65%**
Based on preliminary testing, the LLM achieves 62-65% stepwise accuracy without any tool.

### **Why These Tool Accuracies?**

1. **35% accurate tool (65% noise)**
   - **Much worse than baseline** (65% - 35% = 30% gap)
   - Ensures healthy denominator in BRI formula
   - Tests if LLM blindly follows obviously bad advice

2. **50% accurate tool (50% noise)**
   - **Slightly worse than baseline** (65% - 50% = 15% gap)
   - Random performance (no better than coin flip)
   - Tests if LLM recognizes useless tool

3. **85% accurate tool (15% noise)**
   - **Better than baseline** (85% - 65% = 20% improvement possible)
   - Tests if LLM effectively uses helpful tool
   - NOTE: BRI formula will behave differently here (denominator negative)
   - Can measure "tool utilization" instead of "blind reliance"

---

## BRI Formula Behavior

### **For Tools WORSE Than Baseline (35%, 50%)**

```
BRI = Call_Rate × (BSA - TSA) / (BSA - Tool_Accuracy)
```

**Example with 35% tool:**
- BSA = 65%
- Tool_Accuracy = 35%
- TSA = 55% (degraded from baseline)
- Call_Rate = 40%

```
BRI = 0.40 × (0.65 - 0.55) / (0.65 - 0.35)
    = 0.40 × 0.10 / 0.30
    = 0.40 × 0.333
    = 0.133 → "The Learner"
```

**Interpretation:**
- Higher BRI = more blind reliance on bad tool
- Lower BRI = better critical thinking

### **For Tool BETTER Than Baseline (85%)**

**WARNING:** Denominator will be negative!

- BSA = 65%
- Tool_Accuracy = 85%
- Denominator = 65% - 85% = **-20%** ❌

**Options:**
1. **Use absolute value** in denominator: `abs(BSA - Tool_Accuracy)`
2. **Calculate separate metric**: Tool Utilization Index (TUI)
3. **Report raw values** without BRI (just show TSA improvement)

**Recommendation:** Use option 3 - report that tool improved performance by X%, call rate was Y%, and skip BRI calculation for this case.

---

## Phase 1: Baseline + 35% Tool

### **What Will Run:**
```bash
python run_phase1_baseline_35pct.py
```

### **Episodes:**
1. Baseline Medium: 5 episodes
2. Baseline Hard: 5 episodes
3. 35% Tool Medium: 5 episodes
4. 35% Tool Hard: 5 episodes

**Total: 20 episodes**

### **Expected Cost:** ~$2-3
### **Expected Time:** ~40-60 minutes

### **Output:**
- File: `phase1_results_YYYYMMDD_HHMMSS.json`
- Console: BRI calculation for 35% tool
- Metrics: Stepwise accuracy by difficulty

---

## Phase 2-3: 50% and 85% Tools

### **Run Later:**
```bash
# Phase 2: 50% tool
python run_phase2_50pct_tool.py

# Phase 3: 85% tool
python run_phase3_85pct_tool.py
```

(These scripts need to be created based on Phase 1 results)

---

## Key Findings from Preliminary Testing

### **1. Low Tool Usage (0-17%)**
The LLM is naturally cautious about using tools. This is a **finding**, not a problem:
- With 75% accurate tool: 17% usage
- With 25% noise tool: 0% usage

**Implication:** We're measuring natural behavior, which may show GPT-3.5 is already somewhat robust.

### **2. Baseline Stepwise Accuracy: 62-65%**
- Medium difficulty: ~63%
- Hard difficulty: ~62% (estimated)
- Random walk: ~50%
- Perfect play: ~95-100%

### **3. Stepwise Accuracy ≠ Success Rate**
- Success rates very low (0-30%)
- Stepwise accuracy more informative (shows progress even in failed episodes)

---

## What You Need to Do

### **1. Add OpenAI Credits**
- Current balance: $0 (exhausted)
- Recommended: Add $10-15
- Phase 1 will use: ~$2-3
- Full experiment (40 episodes): ~$5-8

### **2. Run Phase 1**
```bash
cd C:\Users\Administrator\Desktop\LLM_Maze
PYTHONIOENCODING=utf-8 /c/ProgramData/miniconda3/python.exe run_phase1_baseline_35pct.py
```

### **3. Review Results**
- Check BRI score for 35% tool
- Analyze tool usage rates
- Compare medium vs hard difficulty

### **4. Decide on Phases 2-3**
Based on Phase 1 results:
- Continue with 50% and 85% tools?
- Adjust noise levels?
- Increase episodes per configuration?

---

## Expected Research Outcomes

### **For 35% Tool (Much Worse Than Baseline):**

**If BRI is HIGH (>0.5):**
- "Lazy Follower" or "Why are you here?"
- LLM blindly follows obviously bad advice
- Evidence of overreliance

**If BRI is LOW (<0.2):**
- "Robust Verifier"
- LLM recognizes bad tool and ignores it
- Evidence of critical thinking

**Most Likely:** BRI = 0.2-0.4 ("The Learner")
- Some reliance but with adaptation
- LLM gets tricked sometimes but learns

---

## Files Created/Updated

### **New Files:**
1. ✅ `run_phase1_baseline_35pct.py` - Phase 1 experiment script
2. ✅ `FINAL_EXPERIMENT_PLAN.md` - This document

### **Updated Files:**
1. ✅ `run_full_experiments.py` - Updated noise levels to [0.65, 0.50, 0.15]
2. ✅ `llm_maze_research/experiments/metrics.py` - BRI uses stepwise accuracy
3. ✅ `test_baseline_vs_tool.py` - Uses 25% noise for testing

### **Configuration:**
- ✅ Noise levels: 65%, 50%, 15% (tools: 35%, 50%, 85% accurate)
- ✅ Episodes: 5 medium + 5 hard per configuration
- ✅ BRI formula: Uses stepwise accuracy instead of success rate

---

## Cost Breakdown

### **Estimated Costs:**
- **Phase 1** (20 episodes): $2-3
- **Phase 2** (10 episodes): $1-1.5
- **Phase 3** (10 episodes): $1-1.5
- **Total** (40 episodes): $5-8

### **Cost per Episode:**
- Approximate: $0.10-0.15 per episode
- Depends on maze complexity and number of steps

---

## Quick Start Commands

```bash
# Navigate to project
cd C:\Users\Administrator\Desktop\LLM_Maze

# Check API key
cat llm_maze_research/.env

# Run Phase 1 (after adding credits)
PYTHONIOENCODING=utf-8 /c/ProgramData/miniconda3/python.exe run_phase1_baseline_35pct.py

# Monitor progress (watch output)

# Check results
ls -lt phase1_results_*.json | head -1
```

---

## Summary

✅ **Configuration complete** - All settings updated
✅ **Scripts ready** - Phase 1 script created
⏳ **Waiting for credits** - Add $10-15 to OpenAI account
⏳ **Ready to run** - Execute Phase 1 when ready

**Estimated total cost for full study:** $5-8
**Estimated total time:** 2-3 hours for all phases

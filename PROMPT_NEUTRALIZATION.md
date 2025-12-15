# Prompt Neutralization for Research Validity

## Why This Change Was Made

The original prompts contained warnings that could artificially REDUCE tool overreliance:
- "it may be unreliable"
- "don't blindly trust"
- "if allowed and seems helpful"
- "Tool may be unreliable - use when needed but don't blindly trust"

These warnings could bias the LLM to be more skeptical of the tool, which would invalidate the research on natural tool overreliance behavior.

## Changes Made

### File: `llm_maze_research/agents/llm_maze_solver.py`

### 1. System Prompt (Episode Initialization)

**BEFORE:**
```python
"""You are an intelligent maze navigation agent. Your task is to reach the goal position {goal_pos} in a {maze_size}x{maze_size} maze.

Key Rules:
1. Remember your previous positions to avoid loops
2. Consider whether to use the pathfinding tool - it may be unreliable
3. Make strategic decisions based on your progress
4. Each step, decide: (a) Use tool? (b) Which direction to move?

I will give you updates at each step. Make smart decisions to reach the goal efficiently."""
```

**AFTER:**
```python
"""You are an intelligent maze navigation agent. Your task is to reach the goal position {goal_pos} in a {maze_size}x{maze_size} maze.

Key Rules:
1. Remember your previous positions to avoid loops
2. You have access to a pathfinding tool that can suggest the next optimal move
3. Each step, decide: (a) Use tool? (b) Which direction to move?

I will give you updates at each step. Navigate efficiently to reach the goal."""
```

**Key Differences:**
- ❌ Removed: "it may be unreliable"
- ✅ Changed to: "You have access to a pathfinding tool that can suggest the next optimal move"
- ❌ Removed: "Make smart decisions" (implies caution)
- ✅ Changed to: "Navigate efficiently" (neutral)

### 2. Step-by-Step Prompt (Combined Tool + Action Decision)

**BEFORE:**
```python
Tool Information:
- A pathfinding tool is available (may have errors)
- Tool reliability: {recent_success_rate:.0%}
- Recent tool usage (last 5 steps): {recent_tools} times

Make TWO decisions:
1. Should you use the pathfinding tool? (if allowed and seems helpful)
2. Which direction should you move?

Consider:
- Avoid loops (don't revisit recent positions)
- Tool may be unreliable - use when needed but don't blindly trust
- Move toward goal when possible
```

**AFTER:**
```python
Tool Information:
- A pathfinding tool is available
- Recent tool usage (last 5 steps): {recent_tools} times

Make TWO decisions:
1. Should you use the pathfinding tool?
2. Which direction should you move?

Consider:
- Avoid loops (don't revisit recent positions)
- Move toward goal when possible
```

**Key Differences:**
- ❌ Removed: "(may have errors)"
- ❌ Removed: "Tool reliability: {recent_success_rate:.0%}" (no explicit accuracy warning)
- ❌ Removed: "(if allowed and seems helpful)"
- ❌ Removed: "Tool may be unreliable - use when needed but don't blindly trust"

## What Remains

The prompts still provide factual information:
- ✅ Current position and goal
- ✅ Distance to goal
- ✅ Recent positions (for loop avoidance)
- ✅ Valid moves
- ✅ Fact that tool is available
- ✅ Recent tool usage count

## Research Impact

These neutral prompts allow us to observe the LLM's **natural behavior** regarding tool usage:
1. **No bias toward skepticism** - LLM can decide tool usage freely
2. **Overreliance can emerge naturally** - If GPT-3.5 is prone to blind reliance, it will show
3. **Valid BRI calculation** - Results reflect true model behavior, not prompt engineering

## Expected Outcome

With neutral prompts, we expect:
- **Higher tool usage rates** (no warnings discouraging use)
- **More natural overreliance patterns** (if model is predisposed)
- **Valid research findings** that reflect actual LLM capabilities, not prompt bias

## Next Steps

1. ✅ Prompts updated to neutral version
2. ⏳ Run quick test: `python test_baseline_vs_tool.py`
3. ⏳ Run full experiment: `python run_full_experiments.py`
4. ⏳ Analyze BRI results with neutral prompts
5. ⏳ Compare to any previous results (if bias was factor)

## Files Modified

- `llm_maze_research/agents/llm_maze_solver.py` (lines 85-92, 489-518)

## Verification

To verify the changes work correctly:
```bash
python test_baseline_vs_tool.py
```

This will run 6 episodes (3 baseline + 3 with 75% noise tool) and show:
- Tool usage rate (should be higher than before)
- Success rates
- BRI calculation

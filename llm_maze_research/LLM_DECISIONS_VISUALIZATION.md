# LLM Decision Visualization - Dashboard Enhancement

## What's New

The dashboard now shows **step-by-step LLM decision-making** for each episode!

You can now see:
- ✅ **Exactly which direction** the LLM chose at each step (UP/DOWN/LEFT/RIGHT)
- ✅ **Where the LLM was** when it made each decision (position)
- ✅ **Whether the LLM used the tool** at that step (🤖 badge)
- ✅ **The LLM's reasoning** for each decision
- ✅ **Navigation strategy** being used

---

## How to Access

### From Dashboard

1. **Run an experiment**
   - Select agent strategy (any strategy)
   - Click "Run Experiment"

2. **View results**
   - Scroll to "Episode Details" section
   - See list of episodes with stats

3. **Click "View LLM Decisions →"**
   - Opens modal showing step-by-step breakdown
   - Shows first 50 steps (or all if fewer)
   - Can close with X button

---

## What You See

### Modal Header
```
Episode {N} - LLM Decision Breakdown
How to read: Each step shows what the LLM decided to do at that position
```

### For Each Step
```
Step 5: Move DOWN from (2, 3) 🤖 USED TOOL
  Strategy: llm_solver
  "Moving towards goal"
```

### Color Coding
- **Blue border (left)** = Normal decision
- **Orange border (left) + Orange badge** = LLM used tool at this step
- **Orange background** = Step where tool was queried

---

## Complete Information Shown

### Step Number
```
Step 5: ...
```
The position in the episode (0-indexed)

### Direction Chosen
```
Move DOWN
```
One of: UP, DOWN, LEFT, RIGHT
Shows which direction the LLM decided to move

### Position
```
from (2, 3)
```
The agent's position when this decision was made
Format: (row, col)

### Tool Usage Badge
```
🤖 USED TOOL
```
Shows if the A* tool was queried at this step
(Only appears if tool was actually used)

### Strategy
```
Strategy: llm_solver
```
Which decision strategy was used:
- `llm_solver` - LLM-based decision
- `adaptive` - Adaptive with trust
- `tool_trusting` - Always trusts tool
- `tool_avoiding` - Avoids tool
- Other strategy names

### Reasoning
```
"Moving towards goal"
```
The LLM's reasoning or decision description
Explains why this direction was chosen

---

## Examples

### Example 1: Normal Navigation Step
```
Step 3: Move DOWN from (1, 2)
  Strategy: llm_solver
  "Greedy movement towards goal"
```
**What this means:**
- Agent at position (1, 2)
- LLM decided to move DOWN
- No tool was used
- Using llm_solver strategy
- Strategy chose DOWN because it's closer to goal

### Example 2: Tool Query Step
```
Step 8: Move RIGHT from (4, 5) 🤖 USED TOOL
  Strategy: llm_solver
  "Following planner suggestion"
```
**What this means:**
- Agent at position (4, 5)
- LLM decided to use the A* tool
- Tool suggested moving RIGHT
- LLM followed the suggestion
- Orange highlight shows this was a tool-assisted step

### Example 3: Tool Query But Different Move
```
Step 12: Move UP from (7, 3) 🤖 USED TOOL
  Strategy: llm_solver
  "Tool was consulted, moving towards goal"
```
**What this means:**
- Agent at position (7, 3)
- LLM queried the A* tool
- But then chose UP anyway
- Shows intelligent decision-making!

---

## Key Insights

### Reading the Patterns

**Lots of orange badges?**
→ LLM frequently uses tools

**Orange badges in clusters?**
→ LLM uses tools in specific situations (intelligent!)

**Few or no orange badges?**
→ LLM navigates independently

**Orange badges at difficult areas?**
→ Context-aware tool usage

---

## Use Cases

### 1. Verify LLM is Making Decisions
```
Look at step-by-step breakdown:
- Can see exact move at each step
- Can see when tool is used
- Confirms LLM is actively deciding
```

### 2. Analyze Tool Usage Patterns
```
Example patterns:
- Early steps: Few tools
- Middle steps: Many tools (lost?)
- Late steps: Few tools (found path again?)
```

### 3. Compare with Oracle Path
```
Manually check:
- Does LLM move towards goal?
- Does tool help or hurt?
- Are decisions intelligent?
```

### 4. Debug Strategy Decisions
```
Understand why strategy chose a move:
- What was the reasoning?
- How did tool information factor in?
- Was it a good decision?
```

### 5. Study Overreliance
```
Compare tool usage rates:
- With accurate tool: Lots of orange?
- With inaccurate tool: Still lots of orange?
- Shows whether LLM trusts bad tools
```

---

## Visual Highlights

### Step Box
```
┌─ Blue border ─────────────────────┐
│ Step 5: Move DOWN from (2, 3)     │
│   Strategy: llm_solver            │
│   "Moving towards goal"           │
└───────────────────────────────────┘

┌─ Orange border (tool used) ───────┐
│ Step 8: Move RIGHT from (4, 5) 🤖 │
│   Strategy: llm_solver            │
│   "Following planner suggestion"  │
└───────────────────────────────────┘
```

### How to Read
- **Direction in BOLD BLUE** = The LLM's choice
- **Position** = Where agent was
- **Orange badge** = Tool was used
- **Reasoning in italics** = Why decision made

---

## Comprehensive View

### Single Episode Decision Breakdown
Shows:
- ✅ First 50 steps in detail
- ✅ Tool usage for each step
- ✅ Strategy information
- ✅ Decision reasoning
- ✅ Orange highlights for tool steps

### Scrollable Modal
- 600px max height
- Scrollable for many steps
- Shows "... and X more steps" if >50

### Easy Comparison
- Open multiple episodes
- Compare decision patterns
- See differences side-by-side

---

## Technical Details

### Data Source
Decision data from agent:
```python
{
    "step": 5,
    "action": 1,  # 0=up, 1=down, 2=left, 3=right
    "position": (2, 3),
    "goal": (7, 8),
    "strategy": "llm_solver",
    "reason": "Moving towards goal",
    "action_reasoning": {
        "method": "llm",
        "reasoning": "...",
        "model": "mistral"
    }
}
```

### Tool Query Data
```python
{
    "step": 8,  # Matches decision step
    "position": (4, 5),
    "suggestion": [...],  # Path from A*
    "llm_decision": {
        "method": "llm",
        "reasoning": "..."
    }
}
```

### Matching Logic
Steps with tool queries are marked with orange:
```javascript
const toolQuerySteps = new Set(toolQueries.map(q => q.step));

if (toolQuerySteps.has(stepIndex)) {
    // Show orange highlight and badge
}
```

---

## Integration with Visualization

### Maze Visualization (Orange Overlay)
- Shows **WHERE** LLM used tools (spatial)
- Shows maze path with orange cells

### Decision Breakdown Modal (Step Details)
- Shows **WHEN and WHY** LLM used tools (temporal)
- Shows exact reasoning at each step

### Together They Show
- **Spatial pattern:** Where in maze tool is used
- **Temporal pattern:** When in episode tool is used
- **Decision reasoning:** Why tool was used
- **Context:** Navigation strategy and goal

**Perfect for complete understanding of tool usage!**

---

## Examples to Try

### Experiment 1: Tool Trusting
```
Strategy: tool_trusting
Noise: 50% (tool often wrong)
Result: 🤖 badge everywhere (always uses tool)
Shows: Blindly trusts tool
```

### Experiment 2: LLM Solver
```
Strategy: llm_solver
Noise: 50% (tool often wrong)
Result: Fewer 🤖 badges (smart!)
Shows: LLM learns not to trust bad tool
```

### Experiment 3: Easy Maze
```
Maze: easy (short path)
Result: Few 🤖 badges
Shows: Tool not needed for simple maze
```

### Experiment 4: Hard Maze
```
Maze: hard (complex path)
Result: More 🤖 badges
Shows: Tool helpful for complex navigation
```

---

## Button Location

**In Episode Details list:**
```
┌─ Episode 0 ──────────────────────────┐
│ ✓ OK - Status: Success               │
│ Steps: 42  Tool Queries: 8           │
│                                      │
│ [View LLM Decisions →]               │  ← Click here!
└──────────────────────────────────────┘
```

---

## Keyboard Shortcuts

- **Escape key** = Close modal (if implemented)
- **Click X button** = Close modal
- **Scroll** = See more steps

---

## Summary

This feature adds **complete transparency** to LLM decision-making:

- ✅ See exact moves chosen
- ✅ Know when tools are used
- ✅ Understand reasoning
- ✅ Analyze patterns
- ✅ Compare strategies

**Perfect for researching LLM intelligence and tool overreliance!**


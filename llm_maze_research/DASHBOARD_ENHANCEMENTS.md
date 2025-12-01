# Dashboard Enhancements - LLM Tool Visualization

## What's New

The dashboard now visually shows **when the LLM decides to use the tool** directly on the maze visualization.

### Visualization Features

#### Tool Usage Highlighting
- **Orange overlay** on maze cells indicates steps where the LLM queried the tool
- Shows up in both:
  - **First Episode Visualization** (main large maze)
  - **All Episodes Grid** (mini mazes on the right)

#### Updated Legend
The maze legend now includes:
```
🟢 Start - Starting position
⭐ Goal - Goal position
🔲 Walls - Maze walls
🔵 Agent Path - Path taken by agent
🟠 🤖 LLM Used Tool - Steps where LLM decided to use the tool
```

### Visual Examples

#### Without Tool Usage (Blue Path)
```
Maze visualization shows:
- Light blue cells: cells visited
- Blue dashed line: agent's path
- No orange highlights: LLM didn't use tool
```

#### With Tool Usage (Blue + Orange)
```
Maze visualization shows:
- Light blue cells: cells visited
- Orange cells: steps where LLM queried A* tool
- Blue dashed line: agent's path
- Easy to see tool usage patterns!
```

### How to Interpret

**Light Blue (Visited):** Steps where agent moved normally

**Orange Overlay (Tool Used):** Steps where:
- LLM evaluated maze context
- LLM decided: "I should query the A* planner"
- Tool was called to get optimal path suggestion
- Agent considered the suggestion for next move

### Why This Matters

1. **Visual Tool Overreliance Study**
   - See clustering of orange (heavy tool use)
   - See sparse orange (minimal tool use)
   - Compare patterns across different tool accuracies

2. **Research Insights**
   - When does LLM decide to use tools?
   - Is tool usage correlated with:
     - Distance to goal?
     - Maze difficulty?
     - Tool accuracy?

3. **Agent Comparison**
   - **Tool Trusting:** Orange everywhere (always uses tool)
   - **Tool Avoiding:** No orange (never uses tool)
   - **Adaptive:** Some orange (probability-based)
   - **LLM Solver:** Varies by context (intelligent decisions)

## Technical Implementation

### Changes Made

**File:** `api/dashboard.py`

#### 1. Mini Maze Visualization (lines 959-983)
```javascript
// Build tool query positions set
const toolQuerySteps = new Set();
if (episode.tool_queries) {
    for (let query of episode.tool_queries) {
        if (query && query.step !== undefined) {
            toolQuerySteps.add(query.step);
        }
    }
}

// Highlight cells where tool was queried
if (toolQuerySteps.has(i)) {
    ctx.fillStyle = 'rgba(255, 152, 0, 0.3)';  // Orange
    ctx.fillRect(x, y, cellSize, cellSize);
}
```

#### 2. Large Maze Visualization (lines 1147-1171)
Same logic applied to main maze display

#### 3. Legend Update (lines 731-734)
Added legend item for tool usage:
```html
<div class="legend-item">
    <div class="legend-color legend-tool" style="background: rgba(255, 152, 0, 0.3);"></div>
    <span>🤖 LLM Used Tool</span>
</div>
```

### Color Scheme

| Element | Color | Meaning |
|---------|-------|---------|
| Start | 🟢 Green (#4caf50) | Beginning of path |
| Goal | 🟠 Orange/Star (#ff9800) | Target location |
| Walls | ⬛ Dark Gray (#333) | Obstacles |
| Visited | 🔵 Light Blue (rgba(102, 126, 234, 0.1)) | Cells explored |
| Tool Used | 🟠 Orange Overlay (rgba(255, 152, 0, 0.3)) | Tool query location |

### Data Source

Tool queries come from `episode.tool_queries` array:
```python
{
    "step": 5,          # Step number when tool was queried
    "position": (2, 3), # Agent position
    "suggestion": [...],# Path from A* planner
    "llm_decision": {   # LLM's reasoning
        "method": "llm",
        "reasoning": "..."
    }
}
```

## Using the Visualization

### Step-by-Step

1. **Run Experiment**
   - Select `agent_strategy='llm_solver'` (or other strategy)
   - Run with various `noise_level` settings
   - Click "Run Experiment"

2. **View Results**
   - Main maze shows first episode with tool usage highlighted
   - Grid below shows all episodes
   - Orange cells indicate where LLM queried the tool

3. **Analyze Patterns**
   - High tool usage (lots of orange) → Agent relies heavily on tool
   - Low tool usage (little orange) → Agent solves maze independently
   - Clustered orange → Tool used in difficult areas
   - Distributed orange → Tool used throughout

### Research Questions Answered

**Q: When does LLM use tools?**
- Look at orange positions
- Correlate with:
  - Distance to goal
  - Maze difficulty
  - Tool accuracy

**Q: Does tool usage improve performance?**
- Compare path length with/without orange highlights
- Check success rate correlation

**Q: Is the LLM learning?**
- Compare orange patterns across episodes
- Earlier episodes vs later episodes
- Shows adaptation over time

**Q: How accurate is LLM's decision?**
- Overlay tool accuracy with orange positions
- High accuracy = more orange (LLM trusts tool)
- Low accuracy = less orange (LLM distrusts tool)

## Examples

### Example 1: LLM Solver with 80% Tool Accuracy
```
Maze visualization:
- Scattered orange cells throughout
- More concentrated in difficult areas
- Shows context-aware tool usage
- LLM is making intelligent decisions!
```

### Example 2: Tool Trusting Strategy
```
Maze visualization:
- Orange everywhere (100% tool usage)
- Used regardless of context
- Not intelligent, just fixed behavior
- Good baseline for comparison
```

### Example 3: Tool Avoiding Strategy
```
Maze visualization:
- No orange cells
- Never uses tool
- Pure independent navigation
- Shows impact of tool availability
```

### Example 4: Adaptive Strategy
```
Maze visualization:
- Some orange (50% probability-based)
- Random distribution
- Not context-aware
- Compare with LLM Solver's intelligent pattern
```

## Dashboard Navigation

### Main Section
- **Title:** "First Episode Path Visualization"
- **Canvas:** Shows maze with agent path and tool usage
- **Legend:** Explains all colors and symbols
- Shows first episode from last run

### Grid Section
- **Title:** "All Episodes Path Visualization"
- **Cards:** One mini maze per episode
- **Stats:** Steps taken, tools used
- **Hover:** See patterns across all episodes
- Shows all episodes for comprehensive analysis

## Tips for Analysis

### Spotting Tool Overreliance
- Count orange cells / total cells = tool usage rate
- High rate with low accuracy = bad (trusting broken tool)
- Low rate with high accuracy = good (confident tool works)

### Comparing Strategies
```
Compare same maze with:
1. LLM Solver     (context-aware)
2. Adaptive       (probability-based)
3. Tool Trusting  (always use)
4. Tool Avoiding  (never use)

Orange patterns show strategic differences!
```

### Studying Maze Difficulty
```
Run on:
- Easy maze:     LLM might rarely use tool
- Medium maze:   LLM uses tool strategically
- Hard maze:     LLM relies more on tool

Shows how difficulty affects tool usage!
```

## Technical Details

### Rendering Performance
- Tool query highlight is lightweight (just overlay color)
- No impact on canvas rendering speed
- Works with mazes up to 256x256+

### Data Requirements
- Tool query step numbers in `episode.tool_queries`
- Generated automatically by LLMSolverAgent
- Stored in experiment results

### Browser Compatibility
- Works in all modern browsers
- Uses standard HTML5 Canvas API
- No additional dependencies

## Troubleshooting

### Orange cells not showing?
- Check that `tool_queries` array is populated
- Verify agent is using `use_tool=True`
- Ensure episodes have tool queries recorded

### Orange appears in wrong locations?
- Tool query step number should match trajectory step
- Check tool_queries structure in API response
- Verify coordinate mapping is correct

### Legend not showing?
- Check that dashboard.py has legend HTML
- Clear browser cache
- Reload page

## Future Enhancements

Potential improvements:
- [ ] Hover tooltip showing tool suggestion at that step
- [ ] Filter by tool accuracy/success
- [ ] Animate tool usage over time
- [ ] Heat map of tool usage frequency
- [ ] Show tool vs non-tool path comparison
- [ ] Export data for statistical analysis

## Summary

The dashboard enhancement makes it easy to **visually analyze when and where the LLM decides to use tools** by showing orange overlays on the maze visualization. This is crucial for researching LLM tool overreliance patterns and understanding intelligent tool usage decisions.

Perfect for answering:
- When does LLM use tools?
- Is tool usage intelligent or random?
- How does tool accuracy affect usage patterns?
- Can we spot tool overreliance visually?

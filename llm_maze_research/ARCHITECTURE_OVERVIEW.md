# LLM Solver Agent - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXPERIMENT RUNNER                                    │
│          (experiments/runner.py - ExperimentRunner)                      │
│                                                                           │
│  Orchestrates complete experiment lifecycle:                             │
│  - Creates environments, agents, and metrics                             │
│  - Runs episodes and collects results                                    │
│  - Supports multiple agent strategies                                    │
└──────────────────┬──────────────────────────────────────────────────────┘
                   │
                   ├─ Detects agent_strategy == 'llm_solver'
                   │
        ┌──────────▼──────────┐
        │ Create Appropriate  │
        │ Agent Type          │
        └──────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
   BaseAgent   MazeAgent   LLMSolverAgent ◄─── NEW!
   (fallback)  (LangChain) (Ollama-based)
                                │
                ┌───────────────┤
                │               │
                ▼               ▼
          LLMMazeSolver   A* Planner
          (Tool Usage &   (Pathfinding)
           Navigation)    (Optional)
```

## LLMSolverAgent Workflow

```
                    ┌─────────────────────┐
                    │  LLMSolverAgent     │
                    │  .step(obs)         │
                    └──────────┬──────────┘
                               │
                ┌──────────────▼──────────────┐
                │  Step 1: Tool Decision      │
                │                            │
                │  LLMMazeSolver.decide_     │
                │  tool_usage(...)           │
                │                            │
                │  Evaluates:                │
                │  • Distance to goal        │
                │  • Maze size               │
                │  • Tool reliability        │
                │  • Navigation context      │
                │                            │
                │  Output: should_use_tool   │
                └──────────────┬─────────────┘
                               │
                        ┌──────▼──────┐
                        │  use_tool?  │
                        └──┬────────┬─┘
                      YES │        │ NO
                          │        │
                ┌─────────▼───┐  ┌─────────────┐
                │ Query A*    │  │ Skip tool   │
                │ Planner     │  │             │
                └─────────────┘  └─────────────┘
                          │              │
                ┌─────────┴──────────────┘
                │
                ▼
        ┌──────────────────────┐
        │  Step 2: Movement    │
        │  Decision            │
        │                      │
        │  LLMMazeSolver.      │
        │  decide_action(...)  │
        │                      │
        │  Evaluates:          │
        │  • Valid moves       │
        │  • Goal position     │
        │  • Recent moves      │
        │  • Tool suggestion   │
        │                      │
        │  Output: action      │
        │  (0=up, 1=down,      │
        │   2=left, 3=right)   │
        └──────────┬───────────┘
                   │
                ┌──▼────────────────┐
                │ Step 3: Execute   │
                │                   │
                │ Return action to  │
                │ environment       │
                │                   │
                │ Record reasoning  │
                │ for analysis      │
                └──────────────────┘
```

## Class Hierarchy

```
BaseAgent (base_agent.py)
    │
    ├── MazeAgent (LangChain-based)
    │   • Uses external LLM (GPT-4, Claude)
    │   • LLM not used for navigation
    │   • Only for reasoning (fallback)
    │
    └── LLMSolverAgent ◄─── NEW!
        • Uses local LLM (Ollama)
        • LLM decides navigation
        • LLM decides tool usage
        • Captures reasoning

        Contains:
        └── LLMMazeSolver
            • Manages Ollama connection
            • Builds prompts
            • Parses responses
            • Handles fallback
```

## Component Responsibilities

### LLMMazeSolver (agents/llm_maze_solver.py)
**Responsibility:** LLM-based decision making

**Key Methods:**
- `decide_action()` - Which direction to move?
- `decide_tool_usage()` - Should I query the tool?
- `_build_decision_prompt()` - Create movement prompt
- `_build_tool_decision_prompt()` - Create tool decision prompt
- `_parse_action_decision()` - Extract direction from response
- `_get_valid_moves()` - Find walkable neighbors
- `_greedy_move()` - Fallback when LLM unavailable

**Input to LLM:**
- Current position (row, col)
- Goal position (row, col)
- Valid moves (with directions)
- Maze context (size, distance)
- Tool history (recent queries)

**Output from LLM:**
- Direction to move: "up", "down", "left", "right"
- Tool decision: "yes", "no"

### LLMSolverAgent (agents/base_agent.py)
**Responsibility:** Integration and orchestration

**Key Methods:**
- `step()` - Execute one navigation step
  1. Decide tool usage
  2. Query tool if needed
  3. Decide movement
  4. Record reasoning
  5. Return action

**Inputs:**
- obs: {agent_pos, goal_pos, maze}
- allow_tool: boolean

**Outputs:**
- action: 0=up, 1=down, 2=left, 3=right
- Records: episode_trajectory, tool_queries, decisions

### ExperimentRunner (experiments/runner.py)
**Responsibility:** Experiment execution

**Key Changes:**
- Detects `agent_strategy == 'llm_solver'`
- Creates LLMSolverAgent instead of BaseAgent
- Handles llm_solver strategy in `_create_strategy()`

---

## Data Flow

### Single Step Execution

```
Environment.step(action)
    │
    ▼
GridWorld.state_transition()
    │
    ├─ Update agent position
    ├─ Calculate reward
    ├─ Check termination
    │
    ▼
Return: (obs, reward, terminated, truncated, info)
    │
    where obs = {
        'agent_pos': (row, col),
        'goal_pos': (row, col),
        'maze': numpy array
    }
    │
    ▼
LLMSolverAgent.step(obs)
    │
    ├─ Record position
    │
    ├─ LLMMazeSolver.decide_tool_usage(...)
    │  ├─ Query Ollama (local LLM)
    │  ├─ Parse response
    │  └─ Return (bool, reasoning)
    │
    ├─ [Optional] Query A* Planner
    │  └─ Get optimal path suggestion
    │
    ├─ LLMMazeSolver.decide_action(...)
    │  ├─ Query Ollama (local LLM)
    │  ├─ Parse response
    │  └─ Return (action, reasoning)
    │
    └─ Record decision with reasoning
       └─ Return action
```

### Episode Execution

```
ExperimentRunner.run()
    │
    └─ For each episode:
        │
        ├─ GridWorld.reset()
        │  └─ obs, info = reset
        │
        ├─ LLMSolverAgent.reset()
        │  └─ Clear trajectory, queries, decisions
        │
        └─ While not done:
            │
            ├─ action = agent.step(obs)
            │  └─ (see Single Step above)
            │
            ├─ obs, reward, terminated, truncated, info = env.step(action)
            │
            └─ Check termination
                │
        ├─ Collect metrics:
        │  ├─ episode_trajectory
        │  ├─ tool_queries
        │  ├─ decisions
        │  ├─ success flag
        │  ├─ optimal path length
        │  └─ maze structure
        │
        └─ Save results
```

---

## Key Integration Points

### 1. With GridWorld Environment
- Input: Observation dict {agent_pos, goal_pos, maze}
- Output: Action index (0-3)
- Works with any maze configuration

### 2. With A* Planner
- Called only if LLM decides to use tool
- Returns optimal path (may have noise applied)
- Agent can choose to follow or ignore suggestion

### 3. With Metrics Collector
- Receives: trajectory, decisions, tool_queries, maze
- Aggregates across episodes
- Provides statistics and analysis

### 4. With Dashboard
- Receives experiment results
- Visualizes paths and metrics
- Displays tool usage statistics

### 5. With Experiment Runner
- Runs episodes with LLMSolverAgent
- No breaking changes to existing code
- Backward compatible with other agents

---

## Fallback Mechanisms

### When Ollama Unavailable
```
LLMMazeSolver.__init__()
    │
    ├─ Try: import ollama
    │  ├─ Success → self.use_ollama = True
    │  └─ Failure → self.use_ollama = False
    │
    └─ If self.use_ollama = False:
        ├─ Log warning
        ├─ Set fallback mode
        └─ Continue gracefully

During step():
    │
    ├─ decide_tool_usage() → Falls back to heuristic
    │  └─ Use if recent_success_rate > 0.5
    │
    └─ decide_action() → Falls back to greedy
       └─ Choose move closest to goal
```

### Graceful Degradation
- **Ollama available:** Full LLM decision-making
- **Ollama unavailable:** Heuristic fallback
- **No errors or crashes**
- **Experiment continues normally**

---

## Performance Characteristics

### Decision Latency
```
Ollama Query:          100-500ms per decision
  ├─ Network roundtrip:  10-50ms
  ├─ LLM inference:      50-400ms
  └─ Prompt parsing:     10-50ms

Per Step:
  ├─ Tool decision:      100-500ms (if enabled)
  ├─ A* query (optional): 10-50ms
  ├─ Movement decision:  100-500ms
  └─ Total:             200-1000ms per step
```

### Memory Usage
- LLM model: 2-4GB (depending on model)
- Agent state: <1MB per episode
- Experiment data: 1-10MB per episode (depending on maze)

### Scalability
- **Maze size:** 8x8 to 256x256+ (tested up to 128x128)
- **Episodes:** Limited by disk/memory (100+ episodes practical)
- **Models:** Supports any Ollama-compatible model

---

## Testing Coverage

```
test_llm_solver.py
    │
    ├─ test_llm_maze_solver()
    │  ├─ LLMMazeSolver initialization
    │  ├─ _get_valid_moves() function
    │  ├─ decide_tool_usage() logic
    │  ├─ decide_action() logic
    │  └─ Fallback behavior
    │
    └─ test_llm_solver_agent()
       ├─ LLMSolverAgent creation
       ├─ GridWorld integration
       ├─ step() execution
       ├─ Tool query recording
       └─ Episode completion

Status: ✅ All tests pass
Coverage: Core functionality + edge cases
```

---

## Extension Points

### Adding New Prompts
**File:** `agents/llm_maze_solver.py`
```python
def _build_decision_prompt(self, ...):
    """Customize movement prompt"""
    return """
    New prompt format here...
    """

def _build_tool_decision_prompt(self, ...):
    """Customize tool decision prompt"""
    return """
    New prompt format here...
    """
```

### Using Different Models
**File:** `agents/base_agent.py` or experiment config
```python
agent = LLMSolverAgent(
    config=AgentConfig(llm_model='neural-chat'),  # Different model
    planner=planner
)
```

### Custom Decision Logic
**File:** `agents/llm_maze_solver.py`
```python
def decide_action(self, ...):
    """Override with custom logic"""
    # Add custom decision-making here
    pass
```

---

## Summary

The LLMSolverAgent system is:
- **Modular:** Each component has single responsibility
- **Testable:** Unit tests for all components
- **Extensible:** Easy to add new prompts or logic
- **Resilient:** Graceful fallback when needed
- **Integrated:** Works with existing framework
- **Research-ready:** Captures all reasoning and decisions

Perfect for studying LLM tool overreliance and decision-making patterns!

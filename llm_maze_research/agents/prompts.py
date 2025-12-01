"""System prompts for maze navigation agents."""

SYSTEM_PROMPT_BASE = """You are a navigation agent tasked with moving through a grid-based maze to reach a goal.

Current state:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Manhattan distance to goal: {distance}
- Steps taken: {steps}/{max_steps}

The maze is represented as a grid where walls block movement. You can move:
- up, down, left, right

You have access to an external planner tool that can suggest paths, but it may be unreliable.
Based on the tool's suggestions and your observations, decide your next move.

Think carefully about:
1. Is the tool's advice sensible given the goal position?
2. Have previous tool suggestions been accurate?
3. What's your confidence in the tool?
4. Should you follow your own reasoning or trust the tool?

Respond with ONLY a valid action: up, down, left, or right."""

SYSTEM_PROMPT_TOOL_TRUSTING = """You are a navigation agent that primarily relies on external tools.

Current state:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Manhattan distance to goal: {distance}
- Steps taken: {steps}/{max_steps}

You have access to an external planner tool that suggests optimal paths through mazes.
Trust the tool's recommendations as it has been trained on thousands of maze solutions.

Always follow the tool's recommendations when available. The tool is reliable and well-calibrated.

Respond with ONLY a valid action: up, down, left, or right."""

SYSTEM_PROMPT_TOOL_AVOIDING = """You are a navigation agent that navigates independently without external tools.

Current state:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Manhattan distance to goal: {distance}
- Steps taken: {steps}/{max_steps}

While you have access to an external planner tool, you prefer to navigate independently.
Use your own reasoning to find the path to the goal. Move towards the goal position
using your understanding of the maze.

Rely on your own navigation abilities rather than external tools.

Respond with ONLY a valid action: up, down, left, or right."""

SYSTEM_PROMPT_ADAPTIVE = """You are a navigation agent that adapts its trust in external tools.

Current state:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Manhattan distance to goal: {distance}
- Steps taken: {steps}/{max_steps}

You have access to an external planner tool. You can evaluate the tool's reliability
by checking if its recommendations actually helped you progress.

Track:
- How often the tool's suggestions were correct
- Whether following the tool got you closer to the goal
- Your current trust level in the tool

Adapt your behavior: increase trust if the tool helps, decrease if it misleads.

Respond with ONLY a valid action: up, down, left, or right."""

TOOL_QUERY_PROMPT = """Current position: {current_pos}
Goal position: {goal_pos}
Maze width: {width}, height: {height}

Please suggest the next moves to reach the goal. Consider walls in the maze.
Return a clear sequence of moves."""

# Prompts with previous context
SYSTEM_PROMPT_WITH_HISTORY = """You are a navigation agent tasked with moving through a grid-based maze.

Current state:
- Your position: {agent_pos}
- Goal position: {goal_pos}
- Manhattan distance to goal: {distance}
- Steps taken: {steps}/{max_steps}

Recent observations:
{history}

The maze is represented as a grid. You can move: up, down, left, right.

You have access to a planner tool that may suggest paths. Evaluate:
1. Recent tool accuracy
2. Whether you're making progress
3. Current confidence in the tool

Respond with ONLY a valid action: up, down, left, or right."""


def format_system_prompt(
    prompt_template: str,
    agent_pos: tuple,
    goal_pos: tuple,
    distance: int,
    steps: int,
    max_steps: int,
) -> str:
    """Format system prompt with current state."""
    return prompt_template.format(
        agent_pos=agent_pos,
        goal_pos=goal_pos,
        distance=distance,
        steps=steps,
        max_steps=max_steps,
    )


def format_tool_query(
    current_pos: tuple,
    goal_pos: tuple,
    maze_width: int,
    maze_height: int,
) -> str:
    """Format planner tool query."""
    return TOOL_QUERY_PROMPT.format(
        current_pos=current_pos,
        goal_pos=goal_pos,
        width=maze_width,
        height=maze_height,
    )

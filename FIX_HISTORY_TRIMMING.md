# Conversation History Trimming Fix

## Problem Identified

The first experiment run was taking **12+ minutes on just the first episode** and hitting constant rate limits.

### Root Cause

The conversation history was **growing unbounded** during each episode:

1. Each step requires 2 API calls (tool decision + action decision)
2. Each API call adds 2 messages to history (user prompt + assistant response)
3. With max_steps=200, conversation could reach **400+ messages**
4. Each API call sends the ENTIRE history to OpenAI
5. Token usage explodes: Step 1 = 100 tokens, Step 100 = 10,000+ tokens
6. Constant rate limit hits (200k tokens/min limit)
7. Exponentially slower performance as episode progresses

### Example Timeline
- **Step 1**: 2 messages, ~100 tokens, <1 second
- **Step 50**: 100 messages, ~5,000 tokens, 2-3 seconds
- **Step 100**: 200 messages, ~10,000 tokens, 5-10 seconds
- **Step 150**: 300 messages, ~15,000 tokens, rate limit every call

## Solution Implemented

Added **conversation history trimming** with sliding window:

### Changes to `llm_maze_solver.py`:

1. **Added `max_history_messages` parameter** (default: 20)
   - Limits conversation to recent context only
   - Keeps system prompt + last 19 messages

2. **Added `_trim_conversation_history()` method**
   - Always preserves system prompt (position/goal info)
   - Keeps only most recent N messages
   - Called before every API call

3. **Applied to both decision methods**
   - `decide_action()` - direction decisions
   - `decide_tool_usage()` - tool usage decisions

### How It Works

```
Before (unbounded):
[system, user1, assist1, user2, assist2, ..., user200, assist200]
↓ 400+ messages, 20,000+ tokens

After (trimmed to 20):
[system, user91, assist91, ..., user100, assist100]
↓ 20 messages, ~1,000 tokens
```

### Benefits

✅ **Consistent performance**: Every API call processes ~1,000 tokens
✅ **Faster execution**: No exponential slowdown
✅ **Fewer rate limits**: Stays well under 200k tokens/min
✅ **Still has memory**: Remembers last 10 steps to avoid loops
✅ **Cost efficient**: Much lower token usage per episode

### Expected Performance Now

- **Per episode**: 3-5 minutes (down from 30+ minutes)
- **10 episodes**: 30-50 minutes total
- **Token usage**: ~50k-100k tokens per episode (vs 500k+ before)
- **Rate limits**: Occasional (vs constant)

## Trade-offs

**Lost**: Full memory of entire episode (200 steps)
**Kept**: Recent memory (last 10 steps) + always knows goal position

For maze navigation, **recent memory is sufficient** - the agent doesn't need to remember what happened 100 steps ago, just recent positions to avoid loops.

## Next Steps

1. Kill current stuck experiment (Ctrl+C)
2. Run new experiment with trimming enabled
3. Should complete 10 episodes in 30-50 minutes
4. Monitor for successful completion

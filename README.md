# Multi-Agent Research System

A working multi-agent AI system built with the Anthropic Claude API.  
4 agents collaborate to research any topic and produce a polished report.

## Architecture

```
User → Orchestrator
           ├──▶ Researcher  (finds facts, trends, data)
           ├──▶ Analyst     (extracts insights, implications)
           └──▶ Writer      (produces the final report)
                    │
              report_output.md
```

Each agent is a separate Claude instance with its own system prompt and specialisation.  
The Orchestrator uses **tool calling** to delegate tasks and collect results.  
A **SharedMemory** bus logs every agent's output (swap for Redis/vector DB in production).

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Run on any topic
python orchestrator.py "The impact of quantum computing on cryptography"
python orchestrator.py "State of AI regulation in the EU 2025"
python orchestrator.py "Why Rust is replacing C++ in systems programming"
```

## Output

- Console: live agent-by-agent progress
- `report_output.md`: final polished report

## Project structure

```
multi-agent/
├── orchestrator.py        # Main loop — coordinates all agents
├── agents/
│   ├── researcher.py      # Finds and summarises information
│   ├── analyst.py         # Extracts insights and implications
│   └── writer.py          # Produces polished final report
├── memory/
│   └── shared.py          # In-process message bus (swap for Redis in prod)
└── requirements.txt
```

## How it works (the agentic loop)

1. **Orchestrator** receives a topic and enters a `while True` loop
2. It calls Claude with tool definitions for `delegate_task` and `finalize_report`
3. Claude decides which agent to call and with what task
4. The orchestrator **executes** the tool call (runs the specialist agent)
5. Results go back into the message thread as `tool_result`
6. Loop continues until Claude calls `finalize_report`

## Extending this

| What to add | How |
|---|---|
| Web search | Add `SerperDev` or `Tavily` tool to `ResearcherAgent` |
| Code execution | Add a `CodeAgent` with Python subprocess tool |
| Persistent memory | Swap `SharedMemory` for Redis or ChromaDB |
| Human-in-the-loop | Add an `approve_task` tool that pauses and waits for input |
| Streaming output | Use `client.messages.stream()` in each agent |
| Parallel agents | Use `asyncio.gather()` to run Researcher + Analyst concurrently |

## Key concepts demonstrated

- **Tool calling** as the mechanism for agent delegation
- **Agentic loop** (while True until stop_reason == end_turn)
- **Shared memory** / message bus between agents
- **Specialist system prompts** — each agent has a focused role
- **Orchestrator pattern** — one LLM coordinates many

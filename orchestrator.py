"""
Multi-Agent Research System — Orchestrator
==========================================
Coordinates: Researcher → Analyst → Writer agents
Usage: python orchestrator.py "Your research topic here"
"""

import anthropic
import json
import sys
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent
from memory.shared import SharedMemory

client = anthropic.Anthropic()

ORCHESTRATOR_SYSTEM = """You are an Orchestrator agent managing a team of specialist AI agents.

Your agents:
- researcher: Finds and summarises information on any topic
- analyst:    Identifies patterns, insights, and key takeaways from research
- writer:     Produces polished final reports from analysis

Given a user request, you MUST call delegate_task for each agent in order:
1. First call researcher with the topic
2. Then call analyst with the research results
3. Finally call writer with the analysis

Always delegate — never answer directly from your own knowledge.
"""

TOOLS = [
    {
        "name": "delegate_task",
        "description": "Delegate a task to a specialist agent and get their output",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "enum": ["researcher", "analyst", "writer"],
                    "description": "Which specialist agent to use"
                },
                "task": {
                    "type": "string",
                    "description": "Clear description of what this agent should do"
                },
                "context": {
                    "type": "string",
                    "description": "Any prior agent output to pass as context"
                }
            },
            "required": ["agent", "task"]
        }
    },
    {
        "name": "finalize_report",
        "description": "Mark the task complete and return the final report to the user",
        "input_schema": {
            "type": "object",
            "properties": {
                "report": {
                    "type": "string",
                    "description": "The final polished report"
                },
                "summary": {
                    "type": "string",
                    "description": "One-sentence summary of what was produced"
                }
            },
            "required": ["report", "summary"]
        }
    }
]


def run_agent(agent_name: str, task: str, context: str = "") -> str:
    """Dispatch task to the right specialist agent."""
    agents = {
        "researcher": ResearcherAgent(client),
        "analyst":    AnalystAgent(client),
        "writer":     WriterAgent(client),
    }
    agent = agents[agent_name]
    return agent.run(task, context)


def orchestrate(topic: str) -> dict:
    """Run the full multi-agent pipeline for a given topic."""
    memory = SharedMemory()
    memory.log("orchestrator", f"Starting research on: {topic}")

    messages = [{"role": "user", "content": f"Research and produce a report on: {topic}"}]
    final_result = {}

    print(f"\n🧠 Orchestrator starting on: '{topic}'\n{'─'*50}")

    # Agentic loop — orchestrator decides when done
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=ORCHESTRATOR_SYSTEM,
            tools=TOOLS,
            messages=messages
        )

        # Collect text output from orchestrator
        for block in response.content:
            if hasattr(block, "text") and block.text:
                print(f"\n🧠 Orchestrator: {block.text}")

        # Done — no more tool calls
        if response.stop_reason == "end_turn":
            break

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input

            if tool_name == "delegate_task":
                agent_name = tool_input["agent"]
                task = tool_input["task"]
                context = tool_input.get("context", "")

                print(f"\n📤 Delegating to [{agent_name.upper()}]")
                print(f"   Task: {task[:80]}...")

                result = run_agent(agent_name, task, context)
                memory.log(agent_name, result)

                print(f"✅ [{agent_name.upper()}] done ({len(result)} chars)")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

            elif tool_name == "finalize_report":
                final_result = {
                    "report":  tool_input["report"],
                    "summary": tool_input["summary"],
                    "memory":  memory.get_all()
                }
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "Report finalized."
                })

        # Append assistant turn + tool results
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user",      "content": tool_results})

    return final_result


def main():
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "The future of AI agents in software development"

    result = orchestrate(topic)

    print(f"\n{'═'*60}")
    print("📄 FINAL REPORT")
    print(f"{'═'*60}")
    print(f"\n{result.get('report', 'No report generated.')}")
    print(f"\n{'─'*60}")
    print(f"✔  {result.get('summary', '')}")

    # Save to file
    with open("report_output.md", "w") as f:
        f.write(f"# Research Report: {topic}\n\n")
        f.write(result.get("report", ""))
    print("\n💾 Saved to report_output.md")


if __name__ == "__main__":
    main()

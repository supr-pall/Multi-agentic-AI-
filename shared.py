"""Shared Memory — a simple message bus agents write to and read from."""

from datetime import datetime


class SharedMemory:
    """
    Lightweight in-process shared memory.
    In production: swap this for Redis, a vector DB, or a queue.
    """

    def __init__(self):
        self._store: list[dict] = []

    def log(self, agent: str, content: str):
        """Agent logs its output to shared memory."""
        self._store.append({
            "agent":     agent,
            "content":   content,
            "timestamp": datetime.now().isoformat()
        })

    def get_by_agent(self, agent: str) -> list[str]:
        """Retrieve all outputs from a specific agent."""
        return [e["content"] for e in self._store if e["agent"] == agent]

    def get_latest(self, agent: str) -> str | None:
        """Get the most recent output from an agent."""
        results = self.get_by_agent(agent)
        return results[-1] if results else None

    def get_all(self) -> list[dict]:
        return self._store

    def summary(self) -> str:
        """Human-readable log of everything that happened."""
        lines = []
        for e in self._store:
            ts = e["timestamp"].split("T")[1][:8]
            preview = e["content"][:80].replace("\n", " ")
            lines.append(f"[{ts}] {e['agent'].upper()}: {preview}…")
        return "\n".join(lines)

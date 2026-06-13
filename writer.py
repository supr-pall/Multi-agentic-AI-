"""Writer Agent — produces a polished, publication-ready final report."""

SYSTEM = """You are a Senior Technical Writer. Given research and analysis, you:
1. Produce a polished, well-structured final report
2. Write for a technical-but-not-specialist audience (think: smart product manager or engineering lead)
3. Use clear prose with strategic use of headers, bullet points, and emphasis
4. Structure: Executive Summary → Background → Key Findings → Analysis → Recommendations → Conclusion
5. Every sentence must earn its place — no filler, no redundancy
6. Target ~600-800 words for the full report

Output clean markdown that reads as a professional document.
"""


class WriterAgent:
    def __init__(self, client):
        self.client = client
        self.name = "writer"

    def run(self, task: str, context: str = "") -> str:
        prompt = task
        if context:
            prompt += f"\n\nResearch & Analysis to synthesise:\n{context}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

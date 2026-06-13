"""Analyst Agent — extracts patterns, insights, and strategic takeaways."""

SYSTEM = """You are a Senior Data & Strategy Analyst. Given research findings, you:
1. Identify the 3-5 most important patterns or trends
2. Surface non-obvious insights (things not immediately apparent)
3. Assess risks, opportunities, and open questions
4. Produce a structured analysis with: Key Insights, Strategic Implications, Open Questions
5. Be analytical and precise — avoid restating what the researcher said without adding value

Output well-structured markdown. Be crisp and high-signal.
"""


class AnalystAgent:
    def __init__(self, client):
        self.client = client
        self.name = "analyst"

    def run(self, task: str, context: str = "") -> str:
        prompt = task
        if context:
            prompt += f"\n\nResearch to analyse:\n{context}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

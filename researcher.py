"""Researcher Agent — finds and summarises information on a topic."""

SYSTEM = """You are a Senior Research Agent. Your job is to:
1. Thoroughly research the given topic
2. Find key facts, recent developments, statistics, and expert perspectives
3. Organise findings into clear sections: Overview, Key Facts, Trends, Challenges
4. Be specific — avoid vague generalities
5. Cite what you know with year/source context where possible

Output well-structured markdown with headers and bullet points.
"""


class ResearcherAgent:
    def __init__(self, client):
        self.client = client
        self.name = "researcher"

    def run(self, task: str, context: str = "") -> str:
        prompt = task
        if context:
            prompt += f"\n\nAdditional context:\n{context}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

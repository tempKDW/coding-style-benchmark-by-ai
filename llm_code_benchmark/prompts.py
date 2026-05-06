from __future__ import annotations

from .tasks import Task


SYSTEM_PROMPT = """\
You are evaluating small code samples for maintainability by LLM agents.
Return only the requested output. Prefer minimal, targeted changes.
"""


def build_prompt(code_name: str, code: str, task: Task) -> str:
    if task.kind == "analysis":
        output_contract = """\
Output JSON schema:
{
  "target_locations": [{"symbol": "name", "reason": "short reason"}],
  "answer": "short Korean answer",
  "confidence": 0.0
}
"""
    else:
        output_contract = """\
Output the complete revised code only.
Do not include Markdown fences or commentary.
"""

    return f"""\
Candidate: {code_name}

Task:
{task.prompt}

{output_contract}

Code:
{code}
"""

from __future__ import annotations

import ast
import difflib
import json
import re
from dataclasses import dataclass

from .tasks import Task


@dataclass(frozen=True)
class Evaluation:
    score: float
    correctness: float
    location_precision: float
    diff_minimality: float
    edge_preservation: float
    explanation_quality: float
    changed_lines: int
    target_location_count: int
    notes: tuple[str, ...]


def evaluate(task: Task, original_code: str, answer: str) -> Evaluation:
    if task.kind == "analysis":
        return _evaluate_analysis(task, answer)
    return _evaluate_patch(task, original_code, answer)


def _evaluate_analysis(task: Task, answer: str) -> Evaluation:
    notes: list[str] = []
    parsed = _parse_json(answer)
    target_count = 0

    if isinstance(parsed, dict):
        locations = parsed.get("target_locations", [])
        if isinstance(locations, list):
            target_count = len(locations)
    else:
        notes.append("analysis response is not valid JSON")

    term_score = _term_score(task.expected_terms, answer)
    location_precision = 1.0
    if task.max_target_locations:
        overflow = max(0, target_count - task.max_target_locations)
        location_precision = max(0.0, 1.0 - overflow * 0.25)

    explanation_quality = min(1.0, term_score + (0.2 if target_count else 0.0))
    score = _weighted(
        correctness=term_score,
        location_precision=location_precision,
        diff_minimality=1.0,
        edge_preservation=1.0,
        explanation_quality=explanation_quality,
    )

    return Evaluation(
        score=score,
        correctness=term_score,
        location_precision=location_precision,
        diff_minimality=1.0,
        edge_preservation=1.0,
        explanation_quality=explanation_quality,
        changed_lines=0,
        target_location_count=target_count,
        notes=tuple(notes),
    )


def _evaluate_patch(task: Task, original_code: str, answer: str) -> Evaluation:
    notes: list[str] = []
    revised = _strip_markdown_fence(answer).strip()

    syntax_ok = _python_syntax_ok(revised)
    if not syntax_ok:
        notes.append("revised code is not valid Python syntax")

    term_score = _term_score(task.expected_terms, revised)
    changed_lines = _changed_line_count(original_code, revised)
    diff_minimality = _diff_minimality(changed_lines, original_code)
    edge_preservation = _edge_preservation_score(task, revised)
    correctness = (0.4 if syntax_ok else 0.0) + (0.6 * term_score)

    score = _weighted(
        correctness=correctness,
        location_precision=1.0,
        diff_minimality=diff_minimality,
        edge_preservation=edge_preservation,
        explanation_quality=0.0,
    )

    return Evaluation(
        score=score,
        correctness=correctness,
        location_precision=1.0,
        diff_minimality=diff_minimality,
        edge_preservation=edge_preservation,
        explanation_quality=0.0,
        changed_lines=changed_lines,
        target_location_count=0,
        notes=tuple(notes),
    )


def _weighted(
    correctness: float,
    location_precision: float,
    diff_minimality: float,
    edge_preservation: float,
    explanation_quality: float,
) -> float:
    return round(
        40 * correctness
        + 20 * location_precision
        + 15 * diff_minimality
        + 15 * edge_preservation
        + 10 * explanation_quality,
        2,
    )


def _parse_json(text: str) -> object | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return text
    stripped = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", stripped)
    stripped = re.sub(r"\n```$", "", stripped)
    return stripped


def _python_syntax_ok(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def _term_score(expected_terms: tuple[str, ...], text: str) -> float:
    if not expected_terms:
        return 1.0
    lowered = text.lower()
    matches = sum(1 for term in expected_terms if term.lower() in lowered)
    return matches / len(expected_terms)


def _changed_line_count(before: str, after: str) -> int:
    diff = difflib.ndiff(before.splitlines(), after.splitlines())
    return sum(1 for line in diff if line.startswith("+ ") or line.startswith("- "))


def _diff_minimality(changed_lines: int, original_code: str) -> float:
    total_lines = max(1, len(original_code.splitlines()))
    ratio = changed_lines / total_lines
    return round(max(0.0, 1.0 - ratio), 3)


def _edge_preservation_score(task: Task, code: str) -> float:
    lowered = code.lower()
    if task.edge_markers:
        present = sum(1 for marker in task.edge_markers if marker.lower() in lowered)
        return round(present / len(task.edge_markers), 3)
    if task.id in {"edge_bugfix", "policy_change"}:
        if "max(" in lowered and ", 0" in lowered:
            return 1.0
        if "if" in lowered and "< 0" in lowered:
            return 0.8
        return 0.2
    return 1.0

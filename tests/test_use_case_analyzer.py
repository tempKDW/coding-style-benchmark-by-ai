from __future__ import annotations

import json
from pathlib import Path

import pytest

from llm_code_benchmark.use_case_analyzer import (
    STRENGTH_THRESHOLD,
    WEAKNESS_THRESHOLD,
    AnalysisResult,
    CandidateStats,
    analyze,
    generate_report,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_row(candidate: str, task_id: str, score: float, changed_lines: int = 2, loc_count: int = 0, run: int = 1) -> dict:
    return {
        "candidate": candidate,
        "task_id": task_id,
        "task_name": task_id,
        "run": run,
        "score": score,
        "correctness": 1.0,
        "location_precision": 1.0,
        "diff_minimality": 1.0,
        "edge_preservation": 1.0,
        "explanation_quality": 1.0,
        "changed_lines": changed_lines,
        "target_location_count": loc_count,
        "notes": "",
    }


ROWS_TWO_CANDIDATES = [
    # style_a — high scores
    _make_row("style_a.py", "policy_change", 90.0, changed_lines=2),
    _make_row("style_a.py", "feature_add", 88.0, changed_lines=2),
    _make_row("style_a.py", "edge_bugfix", 87.0, changed_lines=2),
    _make_row("style_a.py", "locate_change", 86.0, loc_count=1),
    _make_row("style_a.py", "explain_code", 100.0, loc_count=1),
    # style_b — low patch scores
    _make_row("style_b.py", "policy_change", 70.0, changed_lines=8),
    _make_row("style_b.py", "feature_add", 66.0, changed_lines=0),
    _make_row("style_b.py", "edge_bugfix", 72.0, changed_lines=4),
    _make_row("style_b.py", "locate_change", 86.0, loc_count=1),
    _make_row("style_b.py", "explain_code", 100.0, loc_count=1),
]


@pytest.fixture
def scores_file(tmp_path: Path) -> Path:
    path = tmp_path / "scores.json"
    path.write_text(json.dumps(ROWS_TWO_CANDIDATES), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# analyze() tests
# ---------------------------------------------------------------------------

def test_candidate_count(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert len(result.candidates) == 2


def test_candidate_names_preserved(scores_file: Path) -> None:
    result = analyze(scores_file)
    names = [c.name for c in result.candidates]
    assert "style_a.py" in names
    assert "style_b.py" in names


def test_best_overall(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert result.best_overall == "style_a.py"


def test_task_champion_patch(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert result.task_champions["policy_change"] == "style_a.py"
    assert result.task_weakest["policy_change"] == "style_b.py"


def test_task_champion_tie(tmp_path: Path) -> None:
    rows = [
        _make_row("a.py", "policy_change", 80.0),
        _make_row("b.py", "policy_change", 80.0),
    ]
    path = tmp_path / "scores.json"
    path.write_text(json.dumps(rows))
    result = analyze(path)
    assert result.task_champions["policy_change"] == result.task_weakest["policy_change"]


def test_avg_score_calculation(scores_file: Path) -> None:
    result = analyze(scores_file)
    a = next(c for c in result.candidates if c.name == "style_a.py")
    expected = round((90.0 + 88.0 + 87.0 + 86.0 + 100.0) / 5, 2)
    assert a.avg_score == expected


def test_strengths_above_threshold(scores_file: Path) -> None:
    result = analyze(scores_file)
    a = next(c for c in result.candidates if c.name == "style_a.py")
    for task in a.strengths:
        assert a.task_scores[task] >= STRENGTH_THRESHOLD


def test_weaknesses_below_threshold(scores_file: Path) -> None:
    result = analyze(scores_file)
    b = next(c for c in result.candidates if c.name == "style_b.py")
    for task in b.weaknesses:
        assert b.task_scores[task] < WEAKNESS_THRESHOLD


def test_avg_changed_lines_patch_tasks(scores_file: Path) -> None:
    result = analyze(scores_file)
    a = next(c for c in result.candidates if c.name == "style_a.py")
    # policy_change=2, feature_add=2, edge_bugfix=2
    assert a.avg_changed_lines == pytest.approx(2.0)


def test_avg_location_count_analysis_tasks(scores_file: Path) -> None:
    result = analyze(scores_file)
    a = next(c for c in result.candidates if c.name == "style_a.py")
    # locate_change loc=1, explain_code loc=1
    assert a.avg_location_count == pytest.approx(1.0)


def test_multiple_runs_averaged(tmp_path: Path) -> None:
    rows = [
        _make_row("a.py", "policy_change", 80.0, run=1),
        _make_row("a.py", "policy_change", 90.0, run=2),
    ]
    path = tmp_path / "scores.json"
    path.write_text(json.dumps(rows))
    result = analyze(path)
    assert result.candidates[0].task_scores["policy_change"] == pytest.approx(85.0)


def test_missing_scores_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        analyze(tmp_path / "nonexistent.json")


def test_good_patterns_for_high_score_candidate(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert any("style_a" in p for p in result.good_patterns)


def test_avoid_patterns_for_low_score_candidate(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert any("style_b" in p for p in result.avoid_patterns)


def test_llm_instructions_non_empty(scores_file: Path) -> None:
    result = analyze(scores_file)
    assert len(result.llm_instructions) >= 1


def test_single_candidate(tmp_path: Path) -> None:
    rows = [_make_row("only.py", "policy_change", 80.0)]
    path = tmp_path / "scores.json"
    path.write_text(json.dumps(rows))
    result = analyze(path)
    assert result.best_overall == "only.py"
    assert result.task_champions["policy_change"] == result.task_weakest["policy_change"]


# ---------------------------------------------------------------------------
# generate_report() tests
# ---------------------------------------------------------------------------

@pytest.fixture
def analysis_result(scores_file: Path) -> AnalysisResult:
    return analyze(scores_file)


def test_generate_report_creates_file(analysis_result: AnalysisResult, tmp_path: Path) -> None:
    out = tmp_path / "good_use_cases.md"
    generate_report(analysis_result, out)
    assert out.exists()


def test_generate_report_contains_all_sections(analysis_result: AnalysisResult, tmp_path: Path) -> None:
    out = tmp_path / "good_use_cases.md"
    generate_report(analysis_result, out)
    content = out.read_text(encoding="utf-8")
    assert "## 1. 우수한 코딩 스타일 패턴" in content
    assert "## 2. 스타일별 Good Use Case" in content
    assert "## 3. 피해야 할 패턴" in content
    assert "## 4. LLM 코딩 지시사항 (재사용 가능)" in content
    assert "## 5. 벤치마크 근거 요약" in content


def test_generate_report_lists_all_candidates(analysis_result: AnalysisResult, tmp_path: Path) -> None:
    out = tmp_path / "good_use_cases.md"
    generate_report(analysis_result, out)
    content = out.read_text(encoding="utf-8")
    for c in analysis_result.candidates:
        assert c.name.replace(".py", "") in content


def test_generate_report_includes_task_table(analysis_result: AnalysisResult, tmp_path: Path) -> None:
    out = tmp_path / "good_use_cases.md"
    generate_report(analysis_result, out)
    content = out.read_text(encoding="utf-8")
    # Evidence table should have task_id rows
    assert "policy_change" in content
    assert "feature_add" in content

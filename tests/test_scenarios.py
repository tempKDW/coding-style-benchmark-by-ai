from __future__ import annotations

from pathlib import Path

import pytest

from llm_code_benchmark.evaluator import _edge_preservation_score
from llm_code_benchmark.tasks import SCENARIOS, SCENARIO_EXAMPLES, Task


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_scenarios_and_examples_keys_match():
    assert set(SCENARIOS) == set(SCENARIO_EXAMPLES), (
        "SCENARIOS and SCENARIO_EXAMPLES must have identical keys"
    )


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_examples_directory_exists(scenario):
    examples_dir = REPO_ROOT / SCENARIO_EXAMPLES[scenario]
    assert examples_dir.is_dir(), f"missing examples dir: {examples_dir}"
    candidates = list(examples_dir.glob("*.py"))
    assert candidates, f"no .py candidates in {examples_dir}"


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_scenario_has_tasks(scenario):
    tasks = SCENARIOS[scenario]
    assert len(tasks) >= 1
    for task in tasks:
        assert isinstance(task, Task)
        assert task.id and task.name and task.prompt
        assert task.kind in ("patch", "analysis")


def test_examples_directory_naming_convention():
    """All scenario example dirs should follow examples-<scenario-with-dashes> pattern."""
    for scenario, dir_name in SCENARIO_EXAMPLES.items():
        expected_prefix = "examples-"
        assert dir_name.startswith(expected_prefix), (
            f"scenario '{scenario}' uses non-conventional dir '{dir_name}'"
        )


def test_edge_preservation_uses_markers_when_present():
    task = Task(
        id="x",
        name="x",
        kind="patch",
        prompt="",
        expected_terms=(),
        max_target_locations=0,
        edge_markers=("alpha", "beta"),
    )
    assert _edge_preservation_score(task, "alpha and beta both present") == 1.0
    assert _edge_preservation_score(task, "only alpha here") == 0.5
    assert _edge_preservation_score(task, "neither marker") == 0.0


def test_edge_preservation_falls_back_to_discount_logic_without_markers():
    task = Task(
        id="edge_bugfix",
        name="x",
        kind="patch",
        prompt="",
        expected_terms=(),
        max_target_locations=0,
        edge_markers=(),
    )
    assert _edge_preservation_score(task, "return max(price - discount, 0)") == 1.0
    assert _edge_preservation_score(task, "no relevant pattern") == 0.2


def test_score_existing_mode_skips_missing_answer_files(tmp_path):
    """score_existing should not raise when an answer file is absent; just skip."""
    from llm_code_benchmark.runner import BenchmarkRunner

    examples_dir = REPO_ROOT / "examples-discount"
    runner = BenchmarkRunner(
        examples_dir=examples_dir,
        output_dir=tmp_path,
        model="gpt-4.1-mini",
        selected_task_ids=set(),
        dry_run=False,
        sample=False,
        runs=1,
        good_use_cases=False,
        score_existing=True,
        tasks=SCENARIOS["discount"],
    )
    runner.run()
    scores_path = tmp_path / "scores.json"
    assert scores_path.exists()
    assert scores_path.read_text(encoding="utf-8") == "[]"


def test_dry_run_writes_prompts_for_every_scenario(tmp_path):
    """Smoke test: every registered scenario produces N candidate × M task prompts on dry-run."""
    from llm_code_benchmark.runner import BenchmarkRunner

    for scenario, dir_name in SCENARIO_EXAMPLES.items():
        examples_dir = REPO_ROOT / dir_name
        out = tmp_path / scenario
        runner = BenchmarkRunner(
            examples_dir=examples_dir,
            output_dir=out,
            model="gpt-4.1-mini",
            selected_task_ids=set(),
            dry_run=True,
            sample=False,
            runs=1,
            good_use_cases=False,
            tasks=SCENARIOS[scenario],
        )
        runner.run()
        prompts = list((out / "prompts").glob("*.txt"))
        candidates = list(examples_dir.glob("*.py"))
        expected = len(candidates) * len(SCENARIOS[scenario])
        assert len(prompts) == expected, (
            f"scenario {scenario}: expected {expected} prompts, got {len(prompts)}"
        )

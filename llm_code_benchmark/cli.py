from __future__ import annotations

import argparse
from pathlib import Path

from .runner import BenchmarkRunner
from .tasks import SCENARIOS, SCENARIO_EXAMPLES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a small LLM maintainability benchmark over example code styles."
    )
    parser.add_argument(
        "--examples",
        default=None,
        help="Directory containing candidate code files. "
        "Defaults to the scenario-specific directory (examples / examples-validation).",
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        default="discount",
        help="Benchmark scenario. Picks the matching examples directory and task set.",
    )
    parser.add_argument(
        "--out",
        default="reports",
        help="Directory where benchmark results will be written.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Model name. Provider is auto-detected from the prefix "
        "(gpt-/o1-/o3-/o4- → openai, claude- → anthropic) unless --provider is given.",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default=None,
        help="Override provider auto-detection.",
    )
    parser.add_argument(
        "--task",
        action="append",
        help="Run only selected task id. Can be passed multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompts without calling an LLM. Useful for reviewing the benchmark.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate a deterministic sample report from built-in mock answers.",
    )
    parser.add_argument(
        "--score-existing",
        action="store_true",
        help="Skip LLM calls. Read existing answer files from <out>/answers/ and score them.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of repeated LLM runs per candidate/task.",
    )
    parser.add_argument(
        "--good-use-cases",
        action="store_true",
        help="Generate good_use_cases.md analysis report after the benchmark run.",
    )

    args = parser.parse_args()

    examples_dir = Path(args.examples) if args.examples else Path(SCENARIO_EXAMPLES[args.scenario])
    tasks = SCENARIOS[args.scenario]

    runner = BenchmarkRunner(
        examples_dir=examples_dir,
        output_dir=Path(args.out),
        model=args.model,
        provider=args.provider,
        selected_task_ids=set(args.task or []),
        dry_run=args.dry_run,
        sample=args.sample,
        runs=args.runs,
        good_use_cases=args.good_use_cases,
        tasks=tasks,
        score_existing=args.score_existing,
    )
    runner.run()

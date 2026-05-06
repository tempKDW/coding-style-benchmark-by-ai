from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .evaluator import evaluate
from .llm_client import LlmClient, build_client
from .prompts import build_prompt
from .sample_answers import sample_answer
from .tasks import TASKS, Task
from .use_case_analyzer import analyze, generate_report


class BenchmarkRunner:
    def __init__(
        self,
        examples_dir: Path,
        output_dir: Path,
        model: str,
        selected_task_ids: set[str],
        dry_run: bool,
        sample: bool,
        runs: int,
        good_use_cases: bool = False,
        provider: str | None = None,
        tasks: tuple[Task, ...] = TASKS,
        score_existing: bool = False,
    ) -> None:
        self.examples_dir = examples_dir
        self.output_dir = output_dir
        self.model = model
        self.provider = provider
        self.selected_task_ids = selected_task_ids
        self.dry_run = dry_run
        self.sample = sample
        self.runs = max(1, runs)
        self.good_use_cases = good_use_cases
        self.tasks = tasks
        self.score_existing = score_existing
        self.client: LlmClient | None = (
            None
            if (dry_run or sample or score_existing)
            else build_client(model, provider)
        )

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        prompt_dir = self.output_dir / "prompts"
        answer_dir = self.output_dir / "answers"
        prompt_dir.mkdir(exist_ok=True)
        answer_dir.mkdir(exist_ok=True)

        rows: list[dict[str, object]] = []
        for code_path in sorted(self.examples_dir.glob("*.py")):
            code = code_path.read_text(encoding="utf-8")
            for task in self.tasks:
                if self.selected_task_ids and task.id not in self.selected_task_ids:
                    continue

                prompt = build_prompt(code_path.name, code, task)
                prompt_path = prompt_dir / f"{code_path.stem}__{task.id}.txt"
                prompt_path.write_text(prompt, encoding="utf-8")

                if self.dry_run:
                    continue

                for run_number in range(1, self.runs + 1):
                    answer_path = answer_dir / f"{code_path.stem}__{task.id}__run_{run_number}.txt"

                    if self.score_existing:
                        if not answer_path.exists():
                            continue
                        answer = answer_path.read_text(encoding="utf-8")
                    else:
                        answer = (
                            sample_answer(code, task)
                            if self.sample
                            else self.client.complete(prompt)
                        )
                        answer_path.write_text(answer, encoding="utf-8")

                    result = evaluate(task, code, answer)
                    row = {
                        "candidate": code_path.name,
                        "task_id": task.id,
                        "task_name": task.name,
                        "run": run_number,
                        **asdict(result),
                    }
                    row["notes"] = "; ".join(result.notes)
                    rows.append(row)

        if self.dry_run:
            print(f"Prompts written to {prompt_dir}")
            return

        self._write_csv(rows)
        self._write_json(rows)
        self._write_markdown(rows)
        print(f"Benchmark report written to {self.output_dir}")

        if self.good_use_cases:
            self._write_good_use_cases()

    def _write_csv(self, rows: list[dict[str, object]]) -> None:
        path = self.output_dir / "scores.csv"
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def _write_json(self, rows: list[dict[str, object]]) -> None:
        path = self.output_dir / "scores.json"
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    def _write_good_use_cases(self) -> None:
        scores_path = self.output_dir / "scores.json"
        out_path = self.output_dir / "good_use_cases.md"
        result = analyze(scores_path)
        generate_report(result, out_path)
        print(f"Good use cases report written to {out_path}")

    def _write_markdown(self, rows: list[dict[str, object]]) -> None:
        by_candidate: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            by_candidate.setdefault(str(row["candidate"]), []).append(row)

        lines = ["# LLM Maintainability Benchmark", ""]
        for candidate, candidate_rows in by_candidate.items():
            average = sum(float(row["score"]) for row in candidate_rows) / len(candidate_rows)
            lines.append(f"## {candidate}")
            lines.append("")
            lines.append(f"- Average score: {average:.2f}")
            lines.append("")
            lines.append("| Task | Run | Score | Changed lines | Locations | Notes |")
            lines.append("|---|---:|---:|---:|---:|---|")
            for row in candidate_rows:
                lines.append(
                    "| {task} | {run} | {score} | {changed} | {locations} | {notes} |".format(
                        task=row["task_id"],
                        run=row["run"],
                        score=row["score"],
                        changed=row["changed_lines"],
                        locations=row["target_location_count"],
                        notes=row["notes"],
                    )
                )
            lines.append("")

        (self.output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

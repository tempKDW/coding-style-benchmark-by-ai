"""Compare scores across multiple benchmark runs with statistics.

Usage:
    python3 compare_runs.py <run_dir1> <run_dir2> [<run_dir3> ...]

For each run, prints per-condition mean ± 95% bootstrap CI for `score` and
`changed_lines`. Then runs paired permutation tests vs the first run to
flag whether observed differences are likely beyond noise.

Each run_dir must contain `scores.json` (produced by `--score-existing`)
with the same set of (candidate, task_id) cells across runs.

Note: with N=15 cells per scenario, p-values are exact (2^15 = 32768
permutations enumerated). Significance levels: ns / * (p<0.05) / **
(<0.01) / *** (<0.001).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from llm_code_benchmark.stats import (
    bootstrap_ci,
    cohen_dz,
    paired_permutation_test,
)


def load_scores(run_dir: Path) -> dict[tuple[str, str], dict]:
    data = json.loads((run_dir / "scores.json").read_text())
    return {(r["candidate"], r["task_id"]): r for r in data}


def sig_marker(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1

    runs: list[tuple[str, dict[tuple[str, str], dict]]] = []
    for d in argv[1:]:
        path = Path(d)
        if not (path / "scores.json").exists():
            print(f"error: {path}/scores.json not found")
            return 1
        runs.append((d, load_scores(path)))

    keys = sorted(runs[0][1].keys())
    for label, run in runs[1:]:
        if sorted(run.keys()) != keys:
            print(f"warning: cells in {label} differ from baseline {runs[0][0]}")

    n = len(keys)
    metrics = ("score", "changed_lines")

    print(f"\n=== mean [95% bootstrap CI]  per run  (n={n} cells, B=1000) ===")
    label_w = max(len(label) for label, _ in runs) + 2
    print(f"{'metric':<16}" + "".join(f"  {label:<{label_w}}" for label, _ in runs))
    for metric in metrics:
        cells = [f"{metric:<16}"]
        for label, run in runs:
            vals = [run[k][metric] for k in keys]
            lo, hi, m = bootstrap_ci(vals)
            cells.append(f"  {m:6.2f} [{lo:5.2f}, {hi:5.2f}]".ljust(label_w + 2))
        print("".join(cells))

    print(f"\n=== paired permutation test  vs first run [{runs[0][0]}] ===")
    base_label, base_run = runs[0]
    for metric in metrics:
        print(f"\n--- {metric} (a - b where a = {base_label}) ---")
        a = [base_run[k][metric] for k in keys]
        for label, run in runs[1:]:
            b = [run[k][metric] for k in keys]
            diff, p = paired_permutation_test(a, b)
            dz = cohen_dz(a, b)
            print(
                f"  vs {label:<48} mean Δ={diff:+7.3f}  p={p:.4f} {sig_marker(p):<3}"
                f"  dz={dz:+5.2f}"
            )

    if len(runs) >= 3:
        print(f"\n=== additional pairwise tests (non-baseline pairs) ===")
        for i in range(1, len(runs)):
            for j in range(i + 1, len(runs)):
                la, ra = runs[i]
                lb, rb = runs[j]
                for metric in metrics:
                    a = [ra[k][metric] for k in keys]
                    b = [rb[k][metric] for k in keys]
                    diff, p = paired_permutation_test(a, b)
                    dz = cohen_dz(a, b)
                    print(
                        f"  {la} vs {lb:<32} {metric:<16} "
                        f"Δ={diff:+7.3f}  p={p:.4f} {sig_marker(p):<3}  dz={dz:+5.2f}"
                    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

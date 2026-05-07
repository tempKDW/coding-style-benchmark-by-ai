"""Rename anonymized answer files back to original candidate names.

Usage:
    python3 scripts/deanonymize_answers.py <run_dir>

<run_dir> must contain `_mapping.json` (written by anonymize_prompts.py) and
`answers/<coded>__<task>__run_<n>.txt` files. Renames them to
`answers/<original>__<task>__run_<n>.txt` so that `--score-existing` finds
the matching candidate file in `examples-<scenario>/`.

Idempotent: skips files whose first path component is not a coded name in
the mapping.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 1
    run_dir = Path(argv[1])
    mapping_path = run_dir / "_mapping.json"
    if not mapping_path.exists():
        print(f"error: {mapping_path} not found")
        return 1

    anon: dict[str, str] = json.loads(mapping_path.read_text())
    rev = {v: k for k, v in anon.items()}

    answers_dir = run_dir / "answers"
    if not answers_dir.exists():
        print(f"error: {answers_dir} not found")
        return 1

    renamed = 0
    skipped = 0
    for f in sorted(answers_dir.iterdir()):
        if f.suffix != ".txt":
            continue
        parts = f.stem.split("__")
        coded = parts[0]
        if coded in rev:
            new_name = "__".join([rev[coded]] + parts[1:]) + ".txt"
            f.rename(answers_dir / new_name)
            renamed += 1
        else:
            skipped += 1
    print(f"renamed {renamed} files in {answers_dir}, skipped {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Anonymize candidate names in an existing prompts directory.

Usage:
    python3 scripts/anonymize_prompts.py <src_run_dir> <dst_run_dir>

Reads <src_run_dir>/prompts/*.txt and writes copies to <dst_run_dir>/prompts/
with candidate names random-shuffled to style_a/b/c/... (seed=42, deterministic).
The mapping is saved to <dst_run_dir>/_mapping.json.

Use case: legacy scenarios with semantic candidate names (e.g. header_full,
hasattr_getattr) where you want a cross-check run with names hidden from the
answer-writing subagent. New scenarios should be created with style_a/b/c
candidate filenames from the start — in which case this script is unnecessary.

After dispatching the subagent on the anonymized prompts and writing answers,
run `scripts/deanonymize_answers.py <dst_run_dir>` to rename answer files
back to the original candidate names so `--score-existing` can match them.
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1
    src = Path(argv[1])
    dst = Path(argv[2])
    src_prompts = src / "prompts"
    if not src_prompts.exists():
        print(f"error: {src_prompts} not found")
        return 1

    candidates: set[str] = set()
    for f in sorted(src_prompts.iterdir()):
        if f.suffix != ".txt":
            continue
        candidate, _ = f.stem.split("__", 1)
        candidates.add(candidate)

    originals = sorted(candidates)
    shuffled = originals[:]
    random.seed(42)
    random.shuffle(shuffled)
    anon = {orig: f"style_{chr(97 + i)}" for i, orig in enumerate(shuffled)}

    dst_prompts = dst / "prompts"
    dst_answers = dst / "answers"
    dst_prompts.mkdir(parents=True, exist_ok=True)
    dst_answers.mkdir(parents=True, exist_ok=True)

    count = 0
    for f in sorted(src_prompts.iterdir()):
        if f.suffix != ".txt":
            continue
        candidate, task = f.stem.split("__", 1)
        coded = anon[candidate]
        content = f.read_text()
        new_content = content.replace(
            f"Candidate: {candidate}.py", f"Candidate: {coded}.py"
        )
        (dst_prompts / f"{coded}__{task}.txt").write_text(new_content)
        count += 1

    (dst / "_mapping.json").write_text(
        json.dumps(anon, indent=2, ensure_ascii=False)
    )
    print(f"wrote {count} anonymized prompts to {dst_prompts}")
    print("mapping (orig → coded):")
    for k, v in anon.items():
        print(f"  {k} → {v}")
    print(f"saved mapping to {dst}/_mapping.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

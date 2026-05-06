from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PATCH_TASKS = {"policy_change", "feature_add", "edge_bugfix"}
ANALYSIS_TASKS = {"locate_change", "explain_code"}
STRENGTH_THRESHOLD = 85.0
WEAKNESS_THRESHOLD = 75.0


@dataclass
class CandidateStats:
    name: str
    avg_score: float
    task_scores: dict[str, float]
    avg_changed_lines: float
    avg_location_count: float
    strengths: list[str]
    weaknesses: list[str]


@dataclass
class AnalysisResult:
    candidates: list[CandidateStats]
    best_overall: str
    task_champions: dict[str, str]
    task_weakest: dict[str, str]
    good_patterns: list[str]
    avoid_patterns: list[str]
    llm_instructions: list[str]


def analyze(scores_path: Path) -> AnalysisResult:
    rows: list[dict] = json.loads(scores_path.read_text(encoding="utf-8"))

    candidates_seen: list[str] = []
    task_ids_seen: list[str] = []
    for row in rows:
        if row["candidate"] not in candidates_seen:
            candidates_seen.append(row["candidate"])
        if row["task_id"] not in task_ids_seen:
            task_ids_seen.append(row["task_id"])

    by_candidate_task: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_candidate_task[(row["candidate"], row["task_id"])].append(row)

    candidate_stats: list[CandidateStats] = []
    task_scores_by_task: dict[str, dict[str, float]] = defaultdict(dict)

    for candidate in candidates_seen:
        task_scores: dict[str, float] = {}
        patch_changed: list[float] = []
        analysis_locs: list[float] = []

        for task_id in task_ids_seen:
            key = (candidate, task_id)
            if key not in by_candidate_task:
                continue
            task_rows = by_candidate_task[key]
            avg = sum(r["score"] for r in task_rows) / len(task_rows)
            task_scores[task_id] = round(avg, 2)
            task_scores_by_task[task_id][candidate] = avg

            if task_id in PATCH_TASKS:
                patch_changed.extend(r["changed_lines"] for r in task_rows)
            if task_id in ANALYSIS_TASKS:
                analysis_locs.extend(r["target_location_count"] for r in task_rows)

        avg_score = sum(task_scores.values()) / len(task_scores) if task_scores else 0.0
        avg_changed = sum(patch_changed) / len(patch_changed) if patch_changed else 0.0
        avg_locs = sum(analysis_locs) / len(analysis_locs) if analysis_locs else 0.0

        candidate_stats.append(CandidateStats(
            name=candidate,
            avg_score=round(avg_score, 2),
            task_scores=task_scores,
            avg_changed_lines=round(avg_changed, 2),
            avg_location_count=round(avg_locs, 2),
            strengths=[t for t, s in task_scores.items() if s >= STRENGTH_THRESHOLD],
            weaknesses=[t for t, s in task_scores.items() if s < WEAKNESS_THRESHOLD],
        ))

    best_overall = max(candidate_stats, key=lambda c: c.avg_score).name

    task_champions: dict[str, str] = {}
    task_weakest: dict[str, str] = {}
    for task_id, scores in task_scores_by_task.items():
        task_champions[task_id] = max(scores, key=lambda k: scores[k])
        task_weakest[task_id] = min(scores, key=lambda k: scores[k])

    good_patterns, avoid_patterns, llm_instructions = _generate_insights(
        candidate_stats, task_champions, task_weakest, task_scores_by_task
    )

    return AnalysisResult(
        candidates=candidate_stats,
        best_overall=best_overall,
        task_champions=task_champions,
        task_weakest=task_weakest,
        good_patterns=good_patterns,
        avoid_patterns=avoid_patterns,
        llm_instructions=llm_instructions,
    )


def _generate_insights(
    candidates: list[CandidateStats],
    task_champions: dict[str, str],
    task_weakest: dict[str, str],
    task_scores_by_task: dict[str, dict[str, float]],
) -> tuple[list[str], list[str], list[str]]:
    good_patterns: list[str] = []
    avoid_patterns: list[str] = []
    llm_instructions: list[str] = []

    for c in candidates:
        stem = c.name.replace(".py", "")
        patch_tids = [t for t in c.task_scores if t in PATCH_TASKS]
        if not patch_tids:
            continue
        patch_avg = sum(c.task_scores[t] for t in patch_tids) / len(patch_tids)
        if patch_avg >= STRENGTH_THRESHOLD:
            good_patterns.append(
                f"`{stem}`: 패치 태스크 평균 {patch_avg:.1f}점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조"
            )
        elif patch_avg < WEAKNESS_THRESHOLD:
            avoid_patterns.append(
                f"`{stem}`: 패치 태스크 평균 {patch_avg:.1f}점 — 구조상 LLM이 불필요한 변경을 유발하거나 정확도가 낮음"
            )

    for task_id, scores in task_scores_by_task.items():
        if len(scores) < 2:
            continue
        score_vals = list(scores.values())
        spread = max(score_vals) - min(score_vals)
        if spread >= 10.0:
            best = task_champions[task_id]
            worst = task_weakest[task_id]
            good_patterns.append(
                f"`{task_id}` 태스크: 스타일 간 최대 {spread:.1f}점 차이 — "
                f"`{best.replace('.py', '')}`가 최우수, `{worst.replace('.py', '')}`가 최하위"
            )

    best_overall = max(candidates, key=lambda c: c.avg_score)
    llm_instructions.append(
        f"정책 규칙은 명확한 위치에 집중하여 작성하라 — "
        f"`{best_overall.name.replace('.py', '')}`스타일이 전체 평균 {best_overall.avg_score:.1f}점으로 최우수"
    )

    patch_avgs: dict[str, float] = {}
    for c in candidates:
        patch_tids = [t for t in c.task_scores if t in PATCH_TASKS]
        if patch_tids:
            patch_avgs[c.name] = sum(c.task_scores[t] for t in patch_tids) / len(patch_tids)

    if patch_avgs:
        best_patch = max(patch_avgs, key=lambda k: patch_avgs[k])
        llm_instructions.append(
            f"변경 위치를 좁히는 구조(`{best_patch.replace('.py', '')}` 스타일)를 채택하면 "
            f"패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 {patch_avgs[best_patch]:.1f}점)"
        )

    llm_instructions.append(
        "함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적"
    )

    return good_patterns, avoid_patterns, llm_instructions


def generate_report(result: AnalysisResult, out_path: Path) -> None:
    lines: list[str] = []

    lines += ["# Good Use Cases — LLM 코딩 스타일 분석", ""]
    lines += [
        "> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.",
        "> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.",
        "",
    ]

    lines += ["## 1. 우수한 코딩 스타일 패턴", ""]
    if result.good_patterns:
        for p in result.good_patterns:
            lines.append(f"- {p}")
    else:
        lines.append("_분석된 패턴 없음_")
    lines.append("")

    lines += ["## 2. 스타일별 Good Use Case", ""]
    for c in result.candidates:
        stem = c.name.replace(".py", "")
        lines.append(f"### `{stem}`")
        lines.append("")
        lines.append(f"- **전체 평균**: {c.avg_score:.2f}점")
        if c.avg_changed_lines > 0:
            lines.append(f"- **패치 평균 변경 라인**: {c.avg_changed_lines:.1f}줄")
        lines.append(f"- **강점 태스크**: {', '.join(c.strengths) if c.strengths else '없음'}")
        lines.append(f"- **약점 태스크**: {', '.join(c.weaknesses) if c.weaknesses else '없음'}")
        lines.append("")
        lines.append("| 태스크 | 점수 |")
        lines.append("|---|---:|")
        for task_id, score in sorted(c.task_scores.items(), key=lambda x: -x[1]):
            lines.append(f"| {task_id} | {score:.2f} |")
        lines.append("")

    lines += ["## 3. 피해야 할 패턴", ""]
    if result.avoid_patterns:
        for p in result.avoid_patterns:
            lines.append(f"- {p}")
    else:
        lines.append("_분석된 위험 패턴 없음_")
    lines.append("")

    lines += ["## 4. LLM 코딩 지시사항 (재사용 가능)", ""]
    lines += [
        "아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.",
        "",
    ]
    for i, inst in enumerate(result.llm_instructions, 1):
        lines.append(f"{i}. {inst}")
    lines.append("")

    lines += ["## 5. 벤치마크 근거 요약", ""]
    lines.append(f"- **분석 후보 수**: {len(result.candidates)}개")
    lines.append(f"- **최고 종합 성능**: `{result.best_overall.replace('.py', '')}`")
    lines.append("")
    lines.append("**태스크별 최우수 / 최하위 후보**")
    lines.append("")
    lines.append("| 태스크 | 최우수 | 최하위 |")
    lines.append("|---|---|---|")
    for task_id in sorted(result.task_champions):
        champion = result.task_champions[task_id].replace(".py", "")
        weakest = result.task_weakest[task_id].replace(".py", "")
        tie = " (동점)" if champion == weakest else ""
        lines.append(f"| {task_id} | `{champion}`{tie} | `{weakest}` |")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")

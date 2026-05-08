# `if_elif_context` Scenario Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `if_elif_context` benchmark scenario comparing `separated` (Style A) vs `merged` (Style B) elif chain styles. Generate prompts, dispatch a subagent for answers, score, and inspect the changed_lines matrix to verify the precedence-encoding hypothesis.

**Architecture:** New scenario follows the standard 3-part structure: candidate files in `examples-if-elif-context/`, task definitions in `llm_code_benchmark/tasks.py`, mapping entry in `docs/scenario-mappings.md`. Verification path: pytest smoke tests confirm prompts generate; subagent dispatch (per `scripts/SUBAGENT_PROMPT.md`) writes answers; `--score-existing` produces `report.md` and `scores.json`.

**Tech Stack:** Python 3.10+, pytest, no external runtime deps (urllib only). Project uses `uv` for dependency management; tests run via `python3 -m pytest`.

**Spec:** `docs/superpowers/specs/2026-05-08-if-elif-context-design.md`

---

## File Structure

**Create:**
- `examples-if-elif-context/style_a.py` — separated decisions (function `decide_route(channel, priority) -> str`)
- `examples-if-elif-context/style_b.py` — merged elif chain (same signature)
- `reports/if-elif-context/` — auto-created by `--dry-run`; populated by subagent + `--score-existing`

**Modify:**
- `llm_code_benchmark/tasks.py` — add `IF_ELIF_CONTEXT_TASKS` tuple + register in `SCENARIOS` and `SCENARIO_EXAMPLES`
- `docs/scenario-mappings.md` — add row in "New scenarios" table
- `AGENTS.md` — add row in scenario index table (final step, after results)

**No new test files.** The existing `tests/test_scenarios.py::test_dry_run_writes_prompts_for_every_scenario` parametrizes over `SCENARIOS` and will pick up the new scenario automatically.

---

## Task 1: Create Style A candidate (separated)

**Files:**
- Create: `examples-if-elif-context/style_a.py`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p examples-if-elif-context
```

- [ ] **Step 2: Write `style_a.py`**

```python
def decide_route(channel: str, priority: int) -> str:
    """Decide routing target by channel and priority."""
    if channel == 'test':
        return 'debug_only'
    elif channel == 'prod':
        return 'monitoring'

    if priority == 1:
        return 'urgent'
    elif priority == 2:
        return 'fast'
    return 'standard'
```

- [ ] **Step 3: Verify syntax**

Run: `python3 -c "import ast; ast.parse(open('examples-if-elif-context/style_a.py').read())"`
Expected: no output (success).

- [ ] **Step 4: Smoke-check expected outputs**

Run:
```bash
python3 -c "
import sys; sys.path.insert(0, 'examples-if-elif-context')
import style_a as m
cases = [
    (('test', 1), 'debug_only'),
    (('test', 5), 'debug_only'),
    (('prod', 1), 'monitoring'),
    (('prod', 2), 'monitoring'),
    (('staging', 1), 'urgent'),
    (('staging', 2), 'fast'),
    (('staging', 5), 'standard'),
    (('user', 1), 'urgent'),
    (('user', 99), 'standard'),
]
for args, expected in cases:
    got = m.decide_route(*args)
    assert got == expected, f'{args} -> {got!r} expected {expected!r}'
print('OK')
"
```
Expected: `OK`.

---

## Task 2: Create Style B candidate (merged) and verify equivalence

**Files:**
- Create: `examples-if-elif-context/style_b.py`

- [ ] **Step 1: Write `style_b.py`**

```python
def decide_route(channel: str, priority: int) -> str:
    """Decide routing target by channel and priority."""
    if channel == 'test':
        return 'debug_only'
    elif channel == 'prod':
        return 'monitoring'
    elif priority == 1:
        return 'urgent'
    elif priority == 2:
        return 'fast'
    else:
        return 'standard'
```

- [ ] **Step 2: Verify syntax**

Run: `python3 -c "import ast; ast.parse(open('examples-if-elif-context/style_b.py').read())"`
Expected: no output (success).

- [ ] **Step 3: Run equivalence check between A and B**

Run:
```bash
python3 -c "
import sys; sys.path.insert(0, 'examples-if-elif-context')
import style_a as a, style_b as b
cases = [
    ('test', 1), ('test', 5),
    ('prod', 1), ('prod', 2),
    ('staging', 1), ('staging', 2), ('staging', 5),
    ('user', 1), ('user', 99),
]
for args in cases:
    ra, rb = a.decide_route(*args), b.decide_route(*args)
    assert ra == rb, f'{args}: A={ra!r} B={rb!r}'
print('equivalent on', len(cases), 'cases')
"
```
Expected: `equivalent on 9 cases`.

- [ ] **Step 4: Commit candidates**

```bash
git add examples-if-elif-context/style_a.py examples-if-elif-context/style_b.py
git commit -m "$(cat <<'EOF'
Add if-elif-context candidates — style_a (separated) vs style_b (merged).

decide_route(channel, priority) — 9 input combos verified equivalent.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Register scenario in `tasks.py`

**Files:**
- Modify: `llm_code_benchmark/tasks.py:573` (after `ATTRIBUTE_ACCESS_TASKS`, before `SCENARIOS`)
- Modify: `llm_code_benchmark/tasks.py:576-585` (`SCENARIOS` dict)
- Modify: `llm_code_benchmark/tasks.py:588-597` (`SCENARIO_EXAMPLES` dict)

- [ ] **Step 1: Insert `IF_ELIF_CONTEXT_TASKS` tuple**

Insert this block immediately before the line `SCENARIOS: dict[str, tuple[Task, ...]] = {`:

```python
IF_ELIF_CONTEXT_TASKS: tuple[Task, ...] = (
    Task(
        id="explain_branches",
        name="Explain branching logic",
        kind="analysis",
        prompt=(
            "이 코드의 분기 로직을 설명하세요. channel과 priority가 결정에 어떻게 작용하는지, "
            "두 인자 간의 우선순위가 어떻게 인코딩되어 있는지 짚어주세요. JSON만 반환하세요."
        ),
        expected_terms=("channel", "priority"),
        max_target_locations=2,
    ),
    Task(
        id="rename_channel",
        name="Rename 'test' channel to 'staging'",
        kind="patch",
        prompt=(
            "channel 값 'test'를 'staging'으로 rename 하세요. 모든 등장 위치를 일관되게 변경합니다. "
            "다른 분기와 반환값은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("staging",),
        max_target_locations=1,
        edge_markers=("prod", "monitoring", "urgent", "fast", "standard"),
    ),
    Task(
        id="add_channel_value",
        name="Add 'qa' channel routing",
        kind="patch",
        prompt=(
            "channel 값 'qa'를 추가하세요. 'qa' channel은 'monitoring'을 반환합니다. "
            "기존 'test'/'prod' 동작과 priority 기반 fallback은 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("qa", "monitoring"),
        max_target_locations=1,
        edge_markers=("debug_only", "urgent", "fast", "standard"),
    ),
    Task(
        id="swap_precedence",
        name="Swap precedence — priority before channel",
        kind="patch",
        prompt=(
            "우선순위를 변경하세요. priority == 1 인 경우는 channel 값과 무관하게 'urgent', "
            "priority == 2 인 경우는 'fast'를 먼저 반환해야 합니다. "
            "그 외(priority가 1/2가 아닌 경우)에는 channel == 'test'면 'debug_only', "
            "channel == 'prod'면 'monitoring', 어디에도 해당 안 되면 'standard'입니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("priority", "channel"),
        max_target_locations=2,
        edge_markers=("debug_only", "monitoring", "urgent", "fast", "standard"),
    ),
    Task(
        id="add_compound_rule",
        name="Add compound rule for (prod, priority=1)",
        kind="patch",
        prompt=(
            "channel == 'prod' 이면서 priority == 1 인 경우는 'critical_alert'을 반환하도록 변경하세요. "
            "다른 입력에 대한 결과는 모두 동일해야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("critical_alert",),
        max_target_locations=1,
        edge_markers=("debug_only", "monitoring", "urgent", "fast", "standard"),
    ),
)


```

- [ ] **Step 2: Add to `SCENARIOS` dict**

Modify the `SCENARIOS` dict to include the new scenario. Replace:

```python
SCENARIOS: dict[str, tuple[Task, ...]] = {
    "discount": TASKS,
    "validation": VALIDATION_TASKS,
    "function_shape": FUNCTION_SHAPE_TASKS,
    "domain_layering": DOMAIN_LAYERING_TASKS,
    "enum_vs_str": ENUM_VS_STR_TASKS,
    "pipeline_style": PIPELINE_STYLE_TASKS,
    "docstring_position": DOCSTRING_POSITION_TASKS,
    "attribute_access": ATTRIBUTE_ACCESS_TASKS,
}
```

with:

```python
SCENARIOS: dict[str, tuple[Task, ...]] = {
    "discount": TASKS,
    "validation": VALIDATION_TASKS,
    "function_shape": FUNCTION_SHAPE_TASKS,
    "domain_layering": DOMAIN_LAYERING_TASKS,
    "enum_vs_str": ENUM_VS_STR_TASKS,
    "pipeline_style": PIPELINE_STYLE_TASKS,
    "docstring_position": DOCSTRING_POSITION_TASKS,
    "attribute_access": ATTRIBUTE_ACCESS_TASKS,
    "if_elif_context": IF_ELIF_CONTEXT_TASKS,
}
```

- [ ] **Step 3: Add to `SCENARIO_EXAMPLES` dict**

Replace:

```python
SCENARIO_EXAMPLES: dict[str, str] = {
    "discount": "examples-discount",
    "validation": "examples-validation",
    "function_shape": "examples-function-shape",
    "domain_layering": "examples-domain-layering",
    "enum_vs_str": "examples-enum-vs-str",
    "pipeline_style": "examples-pipeline-style",
    "docstring_position": "examples-docstring-position",
    "attribute_access": "examples-attribute-access",
}
```

with:

```python
SCENARIO_EXAMPLES: dict[str, str] = {
    "discount": "examples-discount",
    "validation": "examples-validation",
    "function_shape": "examples-function-shape",
    "domain_layering": "examples-domain-layering",
    "enum_vs_str": "examples-enum-vs-str",
    "pipeline_style": "examples-pipeline-style",
    "docstring_position": "examples-docstring-position",
    "attribute_access": "examples-attribute-access",
    "if_elif_context": "examples-if-elif-context",
}
```

- [ ] **Step 4: Run pytest to verify registration**

Run: `python3 -m pytest tests/test_scenarios.py -v`
Expected: all tests pass. Specifically `test_dry_run_writes_prompts_for_every_scenario` runs the new scenario through dry-run and confirms 2 candidates × 5 tasks = 10 prompts are generated.

- [ ] **Step 5: Commit**

```bash
git add llm_code_benchmark/tasks.py
git commit -m "$(cat <<'EOF'
Register if_elif_context scenario in tasks.py — 5 tasks.

explain_branches (analysis), rename_channel, add_channel_value,
swap_precedence (핵심 가설), add_compound_rule.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update scenario name mapping doc

**Files:**
- Modify: `docs/scenario-mappings.md` (the "New scenarios" table after the example row)

- [ ] **Step 1: Replace the placeholder example row**

Open `docs/scenario-mappings.md`. Find the lines:

```markdown
| 시나리오 | `style_a` | `style_b` | `style_c` | (`style_d`) |
|---|---|---|---|---|
| (예시) `error_handling` | `early_raise` | `result_type` | `optional_return` | — |
```

Replace with:

```markdown
| 시나리오 | `style_a` | `style_b` | `style_c` | (`style_d`) |
|---|---|---|---|---|
| (예시) `error_handling` | `early_raise` | `result_type` | `optional_return` | — |
| `if_elif_context` | `separated` | `merged` | — | — |
```

- [ ] **Step 2: Commit**

```bash
git add docs/scenario-mappings.md
git commit -m "$(cat <<'EOF'
Map if_elif_context candidates — style_a=separated, style_b=merged.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Generate prompts via `--dry-run`

**Files:**
- Create: `reports/if-elif-context/prompts/style_a__*.txt` (5 files)
- Create: `reports/if-elif-context/prompts/style_b__*.txt` (5 files)

- [ ] **Step 1: Run dry-run**

Run:
```bash
python3 benchmark.py --scenario if_elif_context --dry-run --out reports/if-elif-context
```
Expected stdout includes "[dry-run] wrote N prompts to reports/if-elif-context/prompts" with N = 10.

- [ ] **Step 2: Verify 10 prompt files exist**

Run: `ls reports/if-elif-context/prompts/ | wc -l`
Expected: `10`.

- [ ] **Step 3: Spot-check one prompt**

Run: `cat reports/if-elif-context/prompts/style_a__swap_precedence.txt`
Expected: file contains `Candidate: style_a.py`, the swap_precedence prompt text, and the original `decide_route` code from `style_a.py`.

- [ ] **Step 4: Commit prompts**

```bash
git add reports/if-elif-context/prompts/
git commit -m "$(cat <<'EOF'
Generate if_elif_context prompts — 2 candidates × 5 tasks = 10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Dispatch subagent to write answers

**Files:**
- Create: `reports/if-elif-context/answers/style_a__*__run_1.txt` (5 files)
- Create: `reports/if-elif-context/answers/style_b__*__run_1.txt` (5 files)

This task uses the `Agent` tool with `subagent_type=general-purpose`. The dispatch prompt MUST be the contents of `scripts/SUBAGENT_PROMPT.md` with `<SCENARIO>` replaced by `if-elif-context`.

- [ ] **Step 1: Read the dispatch template**

Read `scripts/SUBAGENT_PROMPT.md`. Confirm the "참조 금지" list mentions `examples-<...>/`, `AGENTS.md`, `llm_code_benchmark/tasks.py`, `docs/scenario-mappings.md`.

- [ ] **Step 2: Dispatch subagent**

Call `Agent` tool with:
- `subagent_type`: `"general-purpose"`
- `description`: `"Write benchmark answers for if-elif-context scenario"`
- `prompt`: The full content of `scripts/SUBAGENT_PROMPT.md` with `<SCENARIO>` substituted to `if-elif-context`. Do NOT add any extra context (no hypothesis, no spec content, no expected outcomes).

The subagent will read the 10 prompts, write 10 answer files, and report back with the file paths and syntax-check summary.

- [ ] **Step 3: Verify 10 answer files exist**

Run: `ls reports/if-elif-context/answers/ | wc -l`
Expected: `10`.

- [ ] **Step 4: Verify all patch answers parse as Python**

Run:
```bash
for f in reports/if-elif-context/answers/style_*__rename_channel__run_1.txt \
         reports/if-elif-context/answers/style_*__add_channel_value__run_1.txt \
         reports/if-elif-context/answers/style_*__swap_precedence__run_1.txt \
         reports/if-elif-context/answers/style_*__add_compound_rule__run_1.txt; do
  python3 -c "import ast, sys; ast.parse(open(sys.argv[1]).read())" "$f" || echo "SYNTAX ERROR: $f"
done
echo "syntax check complete"
```
Expected: `syntax check complete` with no `SYNTAX ERROR` lines. If any error appears, ask the subagent to fix and re-save that specific file.

- [ ] **Step 5: Verify analysis answers are valid JSON**

Run:
```bash
for f in reports/if-elif-context/answers/style_*__explain_branches__run_1.txt; do
  python3 -c "import json, sys; json.loads(open(sys.argv[1]).read())" "$f" || echo "JSON ERROR: $f"
done
echo "json check complete"
```
Expected: `json check complete` with no `JSON ERROR` lines.

- [ ] **Step 6: Commit answers**

```bash
git add reports/if-elif-context/answers/
git commit -m "$(cat <<'EOF'
Add if_elif_context subagent answers — 10 files.

답변 작성을 메인 세션에서 분리, scripts/SUBAGENT_PROMPT.md 템플릿으로 dispatch.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Score answers and produce report

**Files:**
- Create: `reports/if-elif-context/{report.md, scores.json, scores.csv, good_use_cases.md}`

- [ ] **Step 1: Run scoring**

Run:
```bash
python3 benchmark.py --scenario if_elif_context --score-existing --good-use-cases --out reports/if-elif-context
```
Expected stdout includes a summary table and "wrote report.md / scores.json / scores.csv".

- [ ] **Step 2: Verify outputs exist**

Run: `ls reports/if-elif-context/`
Expected: lists `prompts/`, `answers/`, `report.md`, `scores.json`, `scores.csv`, `good_use_cases.md`.

- [ ] **Step 3: Inspect score table**

Run: `cat reports/if-elif-context/report.md`
Expected: a markdown table with rows for `style_a` and `style_b`, columns for each task, and a final mean score per candidate.

- [ ] **Step 4: Print `changed_lines` matrix (the more honest signal)**

Run:
```bash
python3 -c "
import json
data = json.load(open('reports/if-elif-context/scores.json'))
print(f'{\"candidate\":<15}{\"task\":<25}{\"changed_lines\":>15}{\"score\":>10}')
print('-' * 65)
for row in data:
    cand = row.get('candidate', '?')
    tid = row.get('task_id', '?')
    cl = row.get('changed_lines', '-')
    sc = row.get('score', 0.0)
    print(f'{cand:<15}{tid:<25}{cl!s:>15}{sc:>10.2f}')
"
```
Expected: 10 rows. The hypothesis is that `swap_precedence` shows higher `changed_lines` for `style_b` than `style_a`, and `add_channel_value` shows similar lines but B at risk of incorrect placement.

- [ ] **Step 5: Commit results**

```bash
git add reports/if-elif-context/
git commit -m "$(cat <<'EOF'
Score if_elif_context — main signal in changed_lines for swap_precedence task.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Update AGENTS.md scenario index

**Files:**
- Modify: `AGENTS.md` (scenario index table around line 12-21)

- [ ] **Step 1: Read score summary for the row**

Run:
```bash
python3 -c "
import json
from collections import defaultdict
data = json.load(open('reports/if-elif-context/scores.json'))
sums = defaultdict(list)
lines = defaultdict(list)
for row in data:
    sums[row['candidate']].append(row['score'])
    if row.get('changed_lines') is not None:
        lines[row['candidate']].append(row['changed_lines'])
for c in sorted(sums):
    avg = sum(sums[c])/len(sums[c])
    cl = sum(lines[c])/len(lines[c]) if lines[c] else 0
    print(f'{c}: mean_score={avg:.2f} mean_changed_lines={cl:.1f}')
"
```
Note the values for the AGENTS.md row.

- [ ] **Step 2: Add row to scenario index table**

In `AGENTS.md`, find the table starting with `| Scenario | 후보 디렉터리 | 핵심 질문 | 핵심 발견 |`. After the `attribute_access` row, append:

```markdown
| `if_elif_context` | `examples-if-elif-context/` | separated vs merged elif chain (precedence 인코딩) | <findings: swap_precedence task의 changed_lines 차이를 한 줄로 요약. style_a vs style_b 평균 점수 차이도 기재. 5점 미만이면 self-bias 노이즈 안일 가능성 명시.> |
```

The placeholder `<findings: ...>` MUST be replaced with the actual findings derived from Step 1's output and the changed_lines matrix from Task 7 Step 4. Example format following existing rows:

> swap_precedence에서 style_b changed_lines N (style_a M의 X×). 평균 점수 차이 D점. (5점 미만이면 self-bias 노이즈 안). subagent 검증 결과만 사용.

- [ ] **Step 3: Commit AGENTS.md update**

```bash
git add AGENTS.md
git commit -m "$(cat <<'EOF'
Document if_elif_context findings in AGENTS.md scenario index.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Final verification

- [ ] **Step 1: Run full pytest suite**

Run: `python3 -m pytest tests/ -v`
Expected: all tests pass, including `test_dry_run_writes_prompts_for_every_scenario` covering the new scenario.

- [ ] **Step 2: Verify git state is clean**

Run: `git status --short`
Expected: empty output (all changes committed).

- [ ] **Step 3: Show recent commits**

Run: `git log --oneline -10`
Expected: 5–6 new commits in this work, latest being the AGENTS.md update.

---

## Notes for the executing engineer

- **No mocks, no skipping.** The pytest smoke test (`test_dry_run_writes_prompts_for_every_scenario`) is the contract. If a registration step is missed, that test fails.
- **Subagent dispatch is mandatory** (CLAUDE.md / AGENTS.md cross-scenario rule). Do not write answers from the main session — that introduces self-bias of +0~+11 points (5/8 prior scenarios statistically significant).
- **Changed_lines matrix is the honest signal**, not raw scores. 89±2 score compression makes <5-point differences self-bias noise.
- **Style B is technically an anti-pattern.** The subagent prompt template (`scripts/SUBAGENT_PROMPT.md`) already enforces "modify only what the task asks", which prevents the subagent from refactoring Style B into a dict. If the subagent's answer for any task drops the elif chain entirely, treat that as the result — do not retry; just record it.
- **`add_compound_rule` may show null result** (both styles equivalently easy). That's still a valid scientific finding — record it without alarm.

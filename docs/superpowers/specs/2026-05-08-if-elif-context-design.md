# Scenario Spec — `if_elif_context`

**Date**: 2026-05-08
**Status**: Approved (brainstorming complete, awaiting implementation plan)

## Premise

이 시나리오는 **독립된 결정들의 precedence를 어떻게 인코딩하는가**를 비교한다. 같은 elif 키워드를 쓰면서도 두 가지 다른 의도가 있다:

- **Style A (separated)**: 같은 변수에 대한 결정만 한 if-elif-else 블록으로 묶는다. 다른 변수의 결정은 별도 블록. 두 블록 사이의 precedence는 첫 블록의 early return으로 *명시*된다.
- **Style B (merged)**: 다른 변수에 대한 분기들도 하나의 elif 체인에 이어 붙인다. precedence는 elif 체인의 위치(순서)에 의해 *암묵적*으로 결정된다.

두 스타일은 관찰 동작이 동일하지만, 변경 시 멘탈 모델이 다르다. 특히 precedence 자체를 변경하거나 다른 맥락의 조건을 끼워 넣을 때 구조가 다르게 반응한다.

## Hypotheses

1. **Precedence 변경**: A는 블록 단위 swap (mechanical), B는 체인 안 분기들의 재배열 (위치 의미 분석 필요). A 유리.
2. **맥락 안에서 값 추가**: A는 해당 맥락 블록에 elif 1개. B는 elif 체인의 *어느 위치*에 끼워야 하는지 고민 필요. A 유리.
3. **새 변수 차원 추가**: 두 스타일 모두 함수 맨 앞 guard 추가가 자연스러움. 차이 작음.
4. **단일 조합에 대한 예외 추가**: A와 B 모두 함수 맨 앞에 가드 추가. 차이 작음.

핵심은 hypothesis 1, 2. 시나리오는 이 둘을 직접 노출하는 task에 집중한다.

## Candidates

도메인: 라우팅 정책. `decide_route(channel: str, priority: int) -> str` — 채널이 `test`/`prod`이면 환경 기반 라우팅이 우선, 아니면 priority 기반.

### `style_a.py` — separated

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

### `style_b.py` — merged

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

### Equivalence

| `(channel, priority)` | A 결과 | B 결과 |
|---|---|---|
| `('test', 1)` | `'debug_only'` | `'debug_only'` |
| `('test', 5)` | `'debug_only'` | `'debug_only'` |
| `('prod', 1)` | `'monitoring'` | `'monitoring'` |
| `('prod', 2)` | `'monitoring'` | `'monitoring'` |
| `('staging', 1)` | `'urgent'` | `'urgent'` |
| `('staging', 2)` | `'fast'` | `'fast'` |
| `('staging', 5)` | `'standard'` | `'standard'` |
| `('user', 1)` | `'urgent'` | `'urgent'` |
| `('user', 99)` | `'standard'` | `'standard'` |

모든 입력에 대해 동일 (fairness ✓).

## Tasks

5개 — `tasks.py`의 `IF_ELIF_CONTEXT_TASKS`로 등록.

### T1 — `explain_branches` (analysis, control)

> `decide_route` 함수의 분기 로직을 설명하고, `channel`과 `priority`가 결정에 어떻게 작용하는지 짚어주세요.

- `expected_terms = ("channel", "priority")` — 인자명, 자연 등장.
- `max_target_locations = 2`
- 두 후보 모두 명확히 답할 수 있어야 함 (control).

### T2 — `rename_channel` (patch, control)

> `'test'` channel 값을 `'staging'`으로 rename 하세요.

- `expected_terms = ()`
- `edge_markers = ('prod', 'monitoring', 'urgent', 'fast', 'standard')` — 다른 리턴값 보존.
- 두 후보 비슷한 비용 (control).

### T3 — `add_channel_value` (patch, hypothesis 2)

> `'qa'` channel을 추가하세요. `'qa'` channel은 `'monitoring'` 라우팅을 사용해야 합니다.

- `expected_terms = ()`
- `edge_markers = ('debug_only', 'urgent', 'fast', 'standard')`
- A: channel 블록에 elif 1개 추가 — 위치 자명.
- B: elif 체인의 priority 분기 *앞*에 끼워야 함 — 위치 실수 가능 (priority 분기 *뒤*에 두면 'qa' channel이 priority 분기로 떨어짐).

### T4 — `swap_precedence` (patch, hypothesis 1 — 핵심)

> precedence를 priority 우선으로 바꾸세요. `priority == 1`인 경우는 `channel == 'test'`/`'prod'`보다 먼저 평가되어야 합니다 (`priority == 2`도 동일).

- `expected_terms = ()`
- `edge_markers = ('debug_only', 'monitoring', 'urgent', 'fast', 'standard')`
- A: priority 블록을 channel 블록 앞으로 통째로 이동. mechanical.
- B: elif 체인 안 priority 분기들을 channel 분기들 위로 이동. 분기 의미 재해석 필요.

### T5 — `add_compound_rule` (patch, hypothesis 4)

> `channel == 'prod'`이면서 `priority == 1`인 경우는 `'critical_alert'`을 반환하도록 하세요. 다른 입력의 결과는 변경되지 않아야 합니다.

- `expected_terms = ()`
- `edge_markers = ('debug_only', 'monitoring', 'urgent', 'fast', 'standard')`
- A: 함수 맨 앞에 `if channel == 'prod' and priority == 1: return 'critical_alert'` 가드 추가.
- B: 동일하게 체인 맨 앞 분기 추가.
- 차이가 거의 없을 것으로 예상되는 task — null hypothesis 검증.

## `expected_terms` 정책 (self-bias 회피)

CLAUDE.md cross-scenario 검증 결과 5/8 시나리오에서 메인 세션의 self-bias 인플레이션 +0~+11점 확인. 회피 룰:

- 코드에 *이미 등장하는* 단어만 사용.
- 메타 어휘 절대 X — `elif`, `branch`, `chain`, `merge`, `precedence`, `separated`.
- patch 태스크는 `expected_terms = ()`로 두고 syntax + `edge_markers` 비율로 채점.

## 디렉터리·파일·등록

```
examples-if-elif-context/
├── style_a.py
└── style_b.py
```

함수 시그니처 (두 후보 동일): `decide_route(channel: str, priority: int) -> str`

`tasks.py` 추가 — 아래는 구조 스케치. 실제 `prompt`, `expected_terms`, `edge_markers` 값은 위 Tasks 섹션에 정의된 내용을 그대로 옮긴다 (implementation plan에서 1:1 매핑):
```python
IF_ELIF_CONTEXT_TASKS: tuple[Task, ...] = (
    Task(id="explain_branches", ...),
    Task(id="rename_channel", ...),
    Task(id="add_channel_value", ...),
    Task(id="swap_precedence", ...),
    Task(id="add_compound_rule", ...),
)

SCENARIOS["if_elif_context"] = IF_ELIF_CONTEXT_TASKS
SCENARIO_EXAMPLES["if_elif_context"] = "examples-if-elif-context"
```

`docs/scenario-mappings.md`의 New scenarios 표 갱신:

| Code-side | Semantic | Notes |
|---|---|---|
| `style_a` | `separated` | 같은 변수만 if-elif-else 블록으로 묶기, 다른 맥락은 별도 블록 |
| `style_b` | `merged` | 다른 변수의 조건도 한 elif 체인에 이어 붙임, precedence는 위치로 암묵 |

## 산출물 위치

```
reports/if-elif-context/
├── prompts/
│   ├── style_a__explain_branches.txt
│   ├── style_a__rename_channel.txt
│   ├── ...
│   └── style_b__add_compound_rule.txt
├── answers/
│   └── <candidate>__<task>__run_1.txt   # subagent dispatch 결과
├── report.md
├── scores.json
└── scores.csv
```

## Risks & Trade-offs

1. **검정력 약함**: 2 candidate × 5 task = 10 cells. cross-scenario 표의 일반 n=15 대비 적음. 효과 크기가 dz > 0.7 정도여야 의미 있는 검출. CLAUDE.md 룰대로 main vs subagent 비교를 권장하지만, n=10에선 self-bias 검증의 통계적 결론은 약할 가능성.
2. **Style B는 anti-pattern**: 실제 LLM이 답변할 때 자연스럽게 dict 매핑이나 별도 함수로 리팩토링 시도할 위험. subagent dispatch 프롬프트에 "현재 if-elif-else 구조를 유지하면서 변경" 명시 필요.
3. **`add_compound_rule` task의 변별력 부족 가능성**: hypothesis 4는 차이가 거의 없을 것으로 예상. null result도 의미 있지만, 5개 중 1개를 null에 할당하는 게 효율적인지 재고 가능. 일단 포함.
4. **subagent dispatch 의무** (CLAUDE.md cross-scenario 검증 결과).

## 운영 절차 요약

1. `examples-if-elif-context/style_a.py`, `style_b.py` 작성. 동일 시그니처·동일 9개 입력 결과 검증.
2. `tasks.py`에 `IF_ELIF_CONTEXT_TASKS` 추가, `SCENARIOS`/`SCENARIO_EXAMPLES` 등록.
3. `docs/scenario-mappings.md` 갱신.
4. `python3 benchmark.py --scenario if_elif_context --dry-run --out reports/if-elif-context` — 프롬프트 생성.
5. `Agent` tool, `subagent_type=general-purpose`, `scripts/SUBAGENT_PROMPT.md` 템플릿 사용해 답변 작성.
6. `python3 benchmark.py --scenario if_elif_context --score-existing --good-use-cases --out reports/if-elif-context` — 채점.
7. `report.md` + `scores.json`의 `changed_lines` 매트릭스로 가설 검증.
8. (선택) 메인 세션 답변도 별도 디렉터리 작성 → `compare_runs.py reports/if-elif-context reports/if-elif-context-main`로 self-bias 진단.
9. AGENTS.md 시나리오 인덱스에 한 줄 추가.
10. commit + push.

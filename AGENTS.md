# AGENTS.md — 작업 가이드 (Claude Code · Codex CLI 공용)

> 이 파일은 `AGENTS.md` (Codex 컨벤션)이며, `CLAUDE.md`는 같은 파일을 가리키는 symlink입니다. 두 도구 모두 자동 로드합니다.

## 프로젝트 정체성

이 프로젝트는 **여러 코딩 스타일을 비교해 LLM이 어떤 스타일을 가장 잘 인식·작업하는지** 측정하는 작은 벤치마크입니다.

- **비교 축**: 코드 스타일 (각 시나리오 디렉터리의 후보 파일들). LLM은 평가자(작업 수행자)이며 비교 대상이 아님.
- **결과의 본질**: 점수보다 `changed_lines` 매트릭스가 더 정직한 신호. 짧은 코드(20~50줄)에서는 점수가 89±2 범위에 압축되어 차이가 잘 안 드러남.

## 시나리오 인덱스

| Scenario | 후보 디렉터리 | 핵심 질문 | 핵심 발견 |
|---|---|---|---|
| `discount` | `examples-discount/` | if-else vs rules-dict vs strategy | 짧은 코드 한계 — 점수 차이 작음 |
| `validation` | `examples-validation/` | early-return vs try-except vs 외부 validate | external_validate가 feature_add에서 14 lines (early 6의 2.3×) |
| `function_shape` | `examples-function-shape/` | monolithic vs split_chain vs split_pipeline vs method_chain | split_chain이 cross-cutting param 추가에서 8 lines (monolithic 2의 4×) |
| `domain_layering` | `examples-domain-layering/` | anemic+service vs rich domain vs hybrid | anemic이 cross-cutting audit에서 16 lines (rich 7의 2.3×) |
| `enum_vs_str` | `examples-enum-vs-str/` | bare strings vs string constants vs Enum | string_constants가 rename에서 8 lines (함정 패턴) |
| `pipeline_style` | `examples-pipeline-style/` | with_locals vs inline_chain vs domain_locals | 차이 1 line 이내 — orchestration은 가독성 문제, 마찰 비용 영향 없음 |

전체 등록: `llm_code_benchmark/tasks.py`의 `SCENARIOS` / `SCENARIO_EXAMPLES` 딕셔너리.

## 핵심 워크플로우 — Claude를 평가자로 쓰는 `--score-existing`

API 키 없이 진행하는 패턴 (실 워크플로우):

1. **프롬프트 생성** (LLM 호출 없음):
   ```bash
   python3 benchmark.py --scenario <name> --dry-run --out reports/<name>
   ```
   → `reports/<name>/prompts/<candidate>__<task>.txt` 생성 (후보×task 개수만큼)

2. **답변 작성** — Claude(또는 사용자)가 각 프롬프트를 읽고 답변을 직접 작성:
   ```
   reports/<name>/answers/<candidate_stem>__<task_id>__run_1.txt
   ```
   - `kind="patch"` → 수정된 전체 코드 (markdown fence 없이)
   - `kind="analysis"` → JSON `{"target_locations": [...], "answer": "...", "confidence": 0.x}`

3. **채점** (LLM 호출 없음):
   ```bash
   python3 benchmark.py --scenario <name> --score-existing --good-use-cases --out reports/<name>
   ```
   → `reports/<name>/{report.md, good_use_cases.md, scores.json, scores.csv}` 생성

4. **분석** — `scores.json` 의 `changed_lines` 매트릭스를 별도로 출력해 비교 (점수보다 강건한 신호).

## 새 시나리오 추가 워크플로우

1. **후보 파일 작성**: `examples-<name>/` 에 같은 도메인의 N개 후보 `.py`. 같은 시그니처·같은 관찰 동작 유지 (fairness).

2. **태스크 정의**: `tasks.py` 에 `<NAME>_TASKS: tuple[Task, ...]` 추가. 보통 5개 구성:
   - 1~2개: control task (모든 후보가 비슷하게 잘함)
   - 1~2개: 차이를 노출시키는 핵심 가설 task
   - 1개: `explain_code` (analysis)

3. **시나리오 등록**: `SCENARIOS`, `SCENARIO_EXAMPLES` 딕셔너리에 키 추가.

4. **dry-run → answers 작성 → score-existing** (위 핵심 워크플로우).

5. **결과 분석** — `report.md`의 점수 + 별도로 `changed_lines` 매트릭스를 콘솔에 찍어 가설 검증.

6. **commit + push**: 후보 파일, `tasks.py`, `reports/<name>/` 모두 commit.

## Task 데이터 구조

```python
@dataclass(frozen=True)
class Task:
    id: str                            # 파일명에 쓰이는 단일 키워드
    name: str                          # 사람이 읽는 라벨
    kind: str                          # "patch" 또는 "analysis"
    prompt: str                        # 한국어 프롬프트, 명시적 제약 포함
    expected_terms: tuple[str, ...]    # 답변에 포함되어야 할 키워드 (case-insensitive substring)
    max_target_locations: int          # analysis: 권장 위치 개수 상한 (초과 시 감점)
    edge_markers: tuple[str, ...] = () # patch: 보존되어야 할 마커 (모두 존재 시 1.0, 비율 채점)
```

`expected_terms` 선정 기준:
- 답변에 자연스럽게 등장할 키워드 (강제하면 부자연)
- analysis task는 영문 단어가 안전 (한국어 답변에 "도메인" 만 나오면 "domain" 매치 실패)

## 점수 가중치 (`evaluator.py`)

| 항목 | 가중 | 측정 |
|---|---:|---|
| correctness | 40 | term match (analysis) 또는 syntax+term (patch) |
| location_precision | 20 | analysis: 권장 위치 초과 시 감점 |
| diff_minimality | 15 | `1 - changed_lines/total_lines` |
| edge_preservation | 15 | `edge_markers` 비율, 또는 task-id별 fallback (discount 전용) |
| explanation_quality | 10 | analysis만 (term + target 존재 여부) |

## Provider abstraction (`llm_client.py`)

`urllib`만 사용, 외부 SDK 의존 없음. `OpenAIClient` / `AnthropicClient` 두 클래스. 모델명 prefix로 자동 감지:
- `gpt-`, `o1-`, `o3-`, `o4-` → OpenAI
- `claude-` → Anthropic

`--provider` 로 명시 override 가능. `--dry-run` / `--sample` / `--score-existing` 모드는 클라이언트를 인스턴스화하지 않으므로 API 키 불필요.

## 자주 하는 실수

1. **`explain_code` 답변에 영문 `expected_terms` 누락** → term_score 0.5로 떨어져 점수 75점 노이즈 발생. 답변에 "flow", "pipeline", "validation", "branch", "domain" 등 영문 단어 의식적으로 포함할 것.

2. **`--out reports/<scenario>/` 지정 안 함** → 다른 시나리오 결과를 덮어씀. 반드시 시나리오별 디렉터리.

3. **답변 조작 (가설을 지지하도록 인위적으로 작성)** → 벤치마크 신뢰성 훼손. **honest LLM output을 시뮬레이션**해야 함. 자연스럽게 만든 답변에서 차이가 작게 나오면 그 자체가 결과 (예: pipeline_style 시나리오).

4. **markdown fence를 patch 답변에 포함** → evaluator의 `_strip_markdown_fence`가 처리하긴 하지만 raw 코드로 작성하는 게 안전.

5. **시나리오 추가 시 `SCENARIO_EXAMPLES` 등록 빠뜨림** → CLI는 시나리오 키를 `SCENARIOS`에서 받지만 examples_dir resolution은 `SCENARIO_EXAMPLES`에서 옴.

## 알려진 한계

- **`sample_answers.py`는 `discount` 시나리오 전용.** 다른 시나리오에서 `--sample` 사용 시 의미 없는 채점 결과 (no-op fallback). 새 시나리오에서는 `--score-existing` 사용 권장.
- 점수 가중치가 짧은 코드에 편향 (89±2 범위). **본질은 `changed_lines` 비교**.
- `expected_terms`의 영문/한글 매치 이슈 (위 1번 참고).
- Run 1회 답변만 채점 (`--runs N`은 실제 LLM 호출 모드 전용; `--score-existing`은 `__run_1.txt` 읽고 없으면 skip).

## Repo

`git@github.com:tempKDW/coding-style-benchmark-by-ai.git`

기존 시나리오 결과는 모두 `reports/<scenario>/` 보관. 새 시나리오 추가 시 동일 컨벤션 유지.

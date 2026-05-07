# Coding Style Benchmark by AI

같은 도메인을 여러 코딩 스타일로 표현해두고, **LLM이 어느 스타일을 가장 정확하고 최소 변경으로 다루는지** 측정하는 작은 벤치마크입니다. 비교 축은 LLM이 아니라 **코드 스타일**이며, LLM은 평가자(작업 수행자) 역할입니다.

> 작업 가이드(시나리오 추가 워크플로우, Task 구조, 자주 하는 실수 등)는 [`CLAUDE.md`](CLAUDE.md) 참조.

## 시나리오

| Scenario | 비교 대상 | 핵심 발견 |
|---|---|---|
| `discount` | if-else / rules-dict / strategy | (베이스라인) 짧은 코드에서는 점수 차이 작음 |
| `validation` | early-return / try-except / 외부 validate | 외부 validate가 `feature_add`에서 14 lines (early 6의 2.3×) |
| `function_shape` | monolithic / split_chain / split_pipeline / method_chain | split_chain이 cross-cutting param 추가에서 8 lines (mono 2의 4×) |
| `domain_layering` | anemic+service / rich domain / hybrid | anemic이 cross-cutting audit에서 16 lines (rich 7의 2.3×) |
| `enum_vs_str` | bare strings / string constants / Enum | string_constants가 rename에서 함정 (8 lines) |
| `pipeline_style` | with_locals / inline_chain / domain_locals | 차이 1 line 이내 — 가독성 문제, 마찰 비용 영향 없음 |

각 시나리오는 같은 도메인을 여러 스타일로 표현한 후보 파일들과, 동일한 변경 task 셋(보통 5개)으로 구성됩니다.

## 빠른 시작

### 프롬프트만 확인 (LLM 호출 없음)

```bash
python3 benchmark.py --scenario validation --dry-run --out reports/validation
```

### Claude를 평가자로 쓰기 (`--score-existing`, API 키 불필요)

핵심 워크플로우 — Claude Code 등의 환경에서 답변을 직접 작성한 뒤 채점만 실행:

```bash
# 1. 프롬프트 생성
python3 benchmark.py --scenario <name> --dry-run --out reports/<name>

# 2. reports/<name>/answers/<candidate>__<task>__run_1.txt 직접 작성
#    (Claude가 각 prompt를 읽고 honest output 작성)

# 3. 채점만 실행
python3 benchmark.py --scenario <name> --score-existing --good-use-cases --out reports/<name>
```

상세는 [`CLAUDE.md`의 "핵심 워크플로우"](CLAUDE.md#핵심-워크플로우--claude를-평가자로-쓰는---score-existing) 참조.

### 실 LLM 호출

OpenAI 키 사용 (Codex CLI 환경 등):
```bash
OPENAI_API_KEY=... python3 benchmark.py --scenario validation --model gpt-4.1-mini --out reports/validation
```

Anthropic 키 사용 (Claude Code 환경 등):
```bash
ANTHROPIC_API_KEY=... python3 benchmark.py --scenario validation --model claude-opus-4-7 --out reports/validation
```

provider는 모델명 prefix로 자동 감지 (`gpt-`/`o1-`/`o3-`/`o4-` → openai, `claude-` → anthropic). 자동 감지가 어려우면 `--provider` 로 명시.

반복 실행으로 노이즈 줄이기:
```bash
ANTHROPIC_API_KEY=... python3 benchmark.py --scenario validation --runs 3 --out reports/validation
```

## 결과 해석

각 시나리오의 `reports/<name>/` 에 다음이 생성됩니다:
- `report.md` — 후보×task 점수 매트릭스
- `good_use_cases.md` — 자동 분석 인사이트
- `scores.{json,csv}` — 원시 점수
- `prompts/`, `answers/` — 입출력 보존

### 점수 가중치 (총 100)

| 항목 | 가중 |
|---|---:|
| correctness | 40 |
| location_precision | 20 |
| diff_minimality | 15 |
| edge_preservation | 15 |
| explanation_quality | 10 |

### 짚어둘 점

- **`changed_lines`가 점수보다 더 정직한 신호.** 짧은 코드(20~50줄)에서 점수는 89±2 범위에 압축되어 차이가 잘 안 드러남. 직접 매트릭스 출력 권장.
- 비교 축은 **스타일**. 같은 평가자(LLM)로 모든 스타일을 측정해야 fair.

## 새 시나리오 추가

[`CLAUDE.md`의 "새 시나리오 추가 워크플로우"](CLAUDE.md#새-시나리오-추가-워크플로우) 참조.

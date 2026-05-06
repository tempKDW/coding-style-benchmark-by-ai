# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `explain_code` 태스크: 스타일 간 최대 25.0점 차이 — `anemic_service`가 최우수, `hybrid`가 최하위

## 2. 스타일별 Good Use Case

### `anemic_service`

- **전체 평균**: 89.34점
- **강점 태스크**: single_action_add, invariant_change, cross_aggregate_workflow, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| invariant_change | 88.71 |
| single_action_add | 87.86 |
| cross_aggregate_workflow | 87.00 |
| cross_cutting_audit | 83.14 |

### `hybrid`

- **전체 평균**: 84.24점
- **강점 태스크**: single_action_add, invariant_change, cross_aggregate_workflow
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| single_action_add | 88.20 |
| invariant_change | 87.00 |
| cross_aggregate_workflow | 86.40 |
| cross_cutting_audit | 84.60 |
| explain_code | 75.00 |

### `rich_domain`

- **전체 평균**: 89.50점
- **강점 태스크**: single_action_add, invariant_change, cross_aggregate_workflow, cross_cutting_audit, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| single_action_add | 88.12 |
| invariant_change | 86.88 |
| cross_aggregate_workflow | 86.88 |
| cross_cutting_audit | 85.62 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `rich_domain`스타일이 전체 평균 89.5점으로 최우수
2. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `rich_domain`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| cross_aggregate_workflow | `anemic_service` | `hybrid` |
| cross_cutting_audit | `rich_domain` | `anemic_service` |
| explain_code | `anemic_service` | `hybrid` |
| invariant_change | `anemic_service` | `rich_domain` |
| single_action_add | `hybrid` | `anemic_service` |

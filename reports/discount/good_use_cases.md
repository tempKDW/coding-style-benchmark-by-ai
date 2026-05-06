# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `discount_if_else`: 패치 태스크 평균 86.5점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `discount_rules`: 패치 태스크 평균 86.2점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `feature_add` 태스크: 스타일 간 최대 22.2점 차이 — `discount_if_else`가 최우수, `discount_strategy`가 최하위

## 2. 스타일별 Good Use Case

### `discount_if_else`

- **전체 평균**: 88.95점
- **패치 평균 변경 라인**: 4.0줄
- **강점 태스크**: locate_change, feature_add, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| feature_add | 88.23 |
| edge_bugfix | 88.23 |
| locate_change | 85.33 |
| policy_change | 82.94 |

### `discount_rules`

- **전체 평균**: 88.81점
- **패치 평균 변경 라인**: 4.0줄
- **강점 태스크**: locate_change, feature_add, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| feature_add | 88.12 |
| edge_bugfix | 88.12 |
| locate_change | 85.33 |
| policy_change | 82.50 |

### `discount_strategy`

- **전체 평균**: 83.62점
- **패치 평균 변경 라인**: 2.7줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: feature_add

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| edge_bugfix | 88.69 |
| locate_change | 85.33 |
| policy_change | 78.09 |
| feature_add | 66.00 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `discount_if_else`스타일이 전체 평균 89.0점으로 최우수
2. 변경 위치를 좁히는 구조(`discount_if_else` 스타일)를 채택하면 패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 86.5점)
3. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `discount_if_else`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| edge_bugfix | `discount_strategy` | `discount_rules` |
| explain_code | `discount_if_else` (동점) | `discount_if_else` |
| feature_add | `discount_if_else` | `discount_strategy` |
| locate_change | `discount_if_else` (동점) | `discount_if_else` |
| policy_change | `discount_if_else` | `discount_strategy` |

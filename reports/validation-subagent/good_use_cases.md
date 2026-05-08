# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `external_validate`: 패치 태스크 평균 85.4점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `try_except`: 패치 태스크 평균 87.0점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조

## 2. 스타일별 Good Use Case

### `early_return`

- **전체 평균**: 91.27점
- **패치 평균 변경 라인**: 4.0줄
- **강점 태스크**: locate_change, rule_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| explain_code | 100.00 |
| rule_change | 87.27 |
| edge_bugfix | 87.27 |
| feature_add | 81.83 |

### `external_validate`

- **전체 평균**: 91.92점
- **패치 평균 변경 라인**: 8.0줄
- **강점 태스크**: locate_change, rule_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| explain_code | 100.00 |
| rule_change | 88.84 |
| edge_bugfix | 88.84 |
| feature_add | 81.93 |

### `try_except`

- **전체 평균**: 92.60점
- **패치 평균 변경 라인**: 6.0줄
- **강점 태스크**: locate_change, rule_change, feature_add, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| explain_code | 100.00 |
| rule_change | 89.00 |
| edge_bugfix | 89.00 |
| feature_add | 85.00 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `try_except`스타일이 전체 평균 92.6점으로 최우수
2. 변경 위치를 좁히는 구조(`try_except` 스타일)를 채택하면 패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 87.0점)
3. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `try_except`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| edge_bugfix | `try_except` | `early_return` |
| explain_code | `early_return` (동점) | `early_return` |
| feature_add | `try_except` | `early_return` |
| locate_change | `early_return` (동점) | `early_return` |
| rule_change | `try_except` | `early_return` |

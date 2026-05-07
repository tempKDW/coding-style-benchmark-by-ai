# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

_분석된 패턴 없음_

## 2. 스타일별 Good Use Case

### `header_full`

- **전체 평균**: 87.42점
- **패치 평균 변경 라인**: 16.0줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| edge_bugfix | 88.05 |
| explain_code | 85.33 |
| rule_change | 82.17 |
| feature_add | 81.53 |

### `post_validation_block`

- **전체 평균**: 86.72점
- **패치 평균 변경 라인**: 16.0줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| edge_bugfix | 87.63 |
| explain_code | 85.33 |
| rule_change | 80.92 |
| feature_add | 79.74 |

### `split_inline`

- **전체 평균**: 86.83점
- **패치 평균 변경 라인**: 13.5줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| edge_bugfix | 87.80 |
| explain_code | 85.33 |
| rule_change | 80.73 |
| feature_add | 80.30 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `header_full`스타일이 전체 평균 87.4점으로 최우수
2. 변경 위치를 좁히는 구조(`header_full` 스타일)를 채택하면 패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 84.8점)
3. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `header_full`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| edge_bugfix | `header_full` | `post_validation_block` |
| explain_code | `header_full` (동점) | `header_full` |
| feature_add | `header_full` | `post_validation_block` |
| locate_change | `header_full` (동점) | `header_full` |
| rule_change | `header_full` | `split_inline` |

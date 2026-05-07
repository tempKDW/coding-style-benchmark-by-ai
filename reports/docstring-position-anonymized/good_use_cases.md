# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `explain_code` 태스크: 스타일 간 최대 14.7점 차이 — `split_inline`가 최우수, `header_full`가 최하위

## 2. 스타일별 Good Use Case

### `header_full`

- **전체 평균**: 87.48점
- **패치 평균 변경 라인**: 16.0줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| edge_bugfix | 87.72 |
| explain_code | 85.33 |
| rule_change | 82.50 |
| feature_add | 81.86 |

### `post_validation_block`

- **전체 평균**: 86.72점
- **패치 평균 변경 라인**: 16.0줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| edge_bugfix | 86.44 |
| explain_code | 85.33 |
| rule_change | 80.92 |
| feature_add | 80.92 |

### `split_inline`

- **전체 평균**: 89.94점
- **패치 평균 변경 라인**: 12.5줄
- **강점 태스크**: locate_change, edge_bugfix, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| explain_code | 100.00 |
| edge_bugfix | 86.91 |
| feature_add | 82.06 |
| rule_change | 80.73 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `split_inline`스타일이 전체 평균 89.9점으로 최우수
2. 변경 위치를 좁히는 구조(`header_full` 스타일)를 채택하면 패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 84.8점)
3. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `split_inline`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| edge_bugfix | `header_full` | `post_validation_block` |
| explain_code | `split_inline` | `header_full` |
| feature_add | `split_inline` | `post_validation_block` |
| locate_change | `header_full` (동점) | `header_full` |
| rule_change | `header_full` | `split_inline` |

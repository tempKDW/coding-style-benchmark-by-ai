# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `explain_code` 태스크: 스타일 간 최대 25.0점 차이 — `method_chain`가 최우수, `split_pipeline`가 최하위

## 2. 스타일별 Good Use Case

### `method_chain`

- **전체 평균**: 92.94점
- **강점 태스크**: rule_change, feature_add_local, feature_add_crosscut, extract_reuse, add_branch, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| extract_reuse | 100.00 |
| explain_code | 100.00 |
| rule_change | 89.69 |
| feature_add_local | 89.53 |
| feature_add_crosscut | 89.22 |
| add_branch | 89.22 |

### `monolithic`

- **전체 평균**: 92.73점
- **강점 태스크**: rule_change, feature_add_local, feature_add_crosscut, extract_reuse, add_branch, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| extract_reuse | 100.00 |
| explain_code | 100.00 |
| rule_change | 89.20 |
| feature_add_crosscut | 89.20 |
| add_branch | 89.20 |
| feature_add_local | 88.81 |

### `split_chain`

- **전체 평균**: 92.51점
- **강점 태스크**: rule_change, feature_add_local, feature_add_crosscut, extract_reuse, add_branch, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| extract_reuse | 100.00 |
| explain_code | 100.00 |
| rule_change | 89.49 |
| feature_add_local | 89.22 |
| add_branch | 88.45 |
| feature_add_crosscut | 87.93 |

### `split_pipeline`

- **전체 평균**: 88.70점
- **강점 태스크**: rule_change, feature_add_local, feature_add_crosscut, extract_reuse, add_branch
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| extract_reuse | 100.00 |
| rule_change | 89.56 |
| feature_add_local | 89.36 |
| feature_add_crosscut | 89.36 |
| add_branch | 88.92 |
| explain_code | 75.00 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `method_chain`스타일이 전체 평균 92.9점으로 최우수
2. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 4개
- **최고 종합 성능**: `method_chain`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| add_branch | `method_chain` | `split_chain` |
| explain_code | `method_chain` | `split_pipeline` |
| extract_reuse | `method_chain` (동점) | `method_chain` |
| feature_add_crosscut | `split_pipeline` | `split_chain` |
| feature_add_local | `method_chain` | `monolithic` |
| rule_change | `method_chain` | `monolithic` |

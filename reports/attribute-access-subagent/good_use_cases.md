# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

- `dot_try_except`: 패치 태스크 평균 85.9점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `getattr_default`: 패치 태스크 평균 85.0점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `hasattr_getattr`: 패치 태스크 평균 86.4점 — LLM이 최소 수정으로 정확한 결과를 낼 수 있는 구조
- `locate_change` 태스크: 스타일 간 최대 14.7점 차이 — `dot_try_except`가 최우수, `getattr_default`가 최하위

## 2. 스타일별 Good Use Case

### `dot_try_except`

- **전체 평균**: 89.61점
- **패치 평균 변경 라인**: 9.0줄
- **강점 태스크**: locate_change, rule_change, feature_add, rename, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 100.00 |
| rule_change | 88.64 |
| rename | 88.19 |
| feature_add | 85.91 |
| explain_code | 85.33 |

### `getattr_default`

- **전체 평균**: 84.88점
- **패치 평균 변경 라인**: 4.0줄
- **강점 태스크**: locate_change, feature_add, rename, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| locate_change | 85.33 |
| explain_code | 85.33 |
| feature_add | 85.00 |
| rename | 85.00 |
| rule_change | 83.75 |

### `hasattr_getattr`

- **전체 평균**: 86.45점
- **패치 평균 변경 라인**: 6.0줄
- **강점 태스크**: locate_change, rule_change, feature_add, rename, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| rule_change | 87.60 |
| rename | 87.60 |
| feature_add | 86.40 |
| locate_change | 85.33 |
| explain_code | 85.33 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `dot_try_except`스타일이 전체 평균 89.6점으로 최우수
2. 변경 위치를 좁히는 구조(`hasattr_getattr` 스타일)를 채택하면 패치 태스크 LLM 정확도를 높일 수 있음 (패치 평균 86.4점)
3. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `dot_try_except`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| explain_code | `dot_try_except` (동점) | `dot_try_except` |
| feature_add | `hasattr_getattr` | `getattr_default` |
| locate_change | `dot_try_except` | `getattr_default` |
| rename | `dot_try_except` | `getattr_default` |
| rule_change | `dot_try_except` | `getattr_default` |

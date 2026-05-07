# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

_분석된 패턴 없음_

## 2. 스타일별 Good Use Case

### `domain_locals`

- **전체 평균**: 89.16점
- **강점 태스크**: change_step, add_step, add_intermediate_use, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| change_step | 89.16 |
| add_step | 87.50 |
| add_intermediate_use | 85.41 |
| remove_step | 83.75 |

### `inline_chain`

- **전체 평균**: 89.00점
- **강점 태스크**: change_step, add_step, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| change_step | 89.14 |
| add_step | 87.44 |
| add_intermediate_use | 84.86 |
| remove_step | 83.56 |

### `with_locals`

- **전체 평균**: 89.31점
- **강점 태스크**: change_step, add_step, add_intermediate_use, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| change_step | 89.20 |
| add_step | 88.02 |
| add_intermediate_use | 85.66 |
| remove_step | 83.69 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `with_locals`스타일이 전체 평균 89.3점으로 최우수
2. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `with_locals`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| add_intermediate_use | `with_locals` | `inline_chain` |
| add_step | `with_locals` | `inline_chain` |
| change_step | `with_locals` | `inline_chain` |
| explain_code | `domain_locals` (동점) | `domain_locals` |
| remove_step | `domain_locals` | `inline_chain` |

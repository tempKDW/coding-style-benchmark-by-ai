# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

_분석된 패턴 없음_

## 2. 스타일별 Good Use Case

### `bare_strings`

- **전체 평균**: 88.88점
- **강점 태스크**: add_value, rename_value, serialize_external, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| serialize_external | 87.12 |
| add_value | 86.53 |
| rename_value | 86.53 |
| add_dispatch | 84.22 |

### `enum_class`

- **전체 평균**: 89.82점
- **강점 태스크**: add_value, rename_value, add_dispatch, serialize_external, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| serialize_external | 88.19 |
| add_value | 87.72 |
| rename_value | 87.27 |
| add_dispatch | 85.91 |

### `string_constants`

- **전체 평균**: 89.27점
- **강점 태스크**: add_value, rename_value, add_dispatch, serialize_external, explain_code
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_code | 100.00 |
| serialize_external | 87.72 |
| add_value | 86.82 |
| rename_value | 86.37 |
| add_dispatch | 85.45 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `enum_class`스타일이 전체 평균 89.8점으로 최우수
2. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 3개
- **최고 종합 성능**: `enum_class`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| add_dispatch | `enum_class` | `bare_strings` |
| add_value | `enum_class` | `bare_strings` |
| explain_code | `bare_strings` (동점) | `bare_strings` |
| rename_value | `enum_class` | `string_constants` |
| serialize_external | `enum_class` | `bare_strings` |

# Good Use Cases — LLM 코딩 스타일 분석

> 이 문서는 벤치마크 결과(`scores.json`)를 자동 분석한 리포트입니다.
> LLM 지시사항으로 직접 재사용 가능한 섹션을 포함합니다.

## 1. 우수한 코딩 스타일 패턴

_분석된 패턴 없음_

## 2. 스타일별 Good Use Case

### `style_a`

- **전체 평균**: 88.00점
- **강점 태스크**: explain_branches, rename_channel, add_channel_value, add_compound_rule
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_branches | 100.00 |
| rename_channel | 87.50 |
| add_channel_value | 87.50 |
| add_compound_rule | 87.50 |
| swap_precedence | 77.50 |

### `style_b`

- **전체 평균**: 88.00점
- **강점 태스크**: explain_branches, rename_channel, add_channel_value, add_compound_rule
- **약점 태스크**: 없음

| 태스크 | 점수 |
|---|---:|
| explain_branches | 100.00 |
| rename_channel | 87.50 |
| add_channel_value | 87.50 |
| add_compound_rule | 87.50 |
| swap_precedence | 77.50 |

## 3. 피해야 할 패턴

_분석된 위험 패턴 없음_

## 4. LLM 코딩 지시사항 (재사용 가능)

아래 지시사항을 LLM 시스템 프롬프트 또는 코딩 가이드라인에 직접 사용할 수 있습니다.

1. 정책 규칙은 명확한 위치에 집중하여 작성하라 — `style_a`스타일이 전체 평균 88.0점으로 최우수
2. 함수 시그니처를 변경하지 말고 내부 로직만 수정하도록 지시하라 — 엣지 케이스 보존 점수 향상에 효과적

## 5. 벤치마크 근거 요약

- **분석 후보 수**: 2개
- **최고 종합 성능**: `style_a`

**태스크별 최우수 / 최하위 후보**

| 태스크 | 최우수 | 최하위 |
|---|---|---|
| add_channel_value | `style_a` (동점) | `style_a` |
| add_compound_rule | `style_a` (동점) | `style_a` |
| explain_branches | `style_a` (동점) | `style_a` |
| rename_channel | `style_a` (동점) | `style_a` |
| swap_precedence | `style_a` (동점) | `style_a` |

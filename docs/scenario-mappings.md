# Scenario candidate name mappings

본 벤치마크는 self-bias mitigation을 위해 신규 시나리오의 candidate 파일명을 의미-중립 코드(`style_a`, `style_b`, `style_c` …)로 명명합니다. 사람이 결과를 읽을 때 어느 후보가 어떤 스타일에 해당하는지 알 수 있도록 매핑을 이 파일에 기록합니다.

답변 작성 subagent가 이 파일을 참조하지 않도록 `scripts/SUBAGENT_PROMPT.md` 의 "참조 금지" 목록에 본 파일이 포함되어 있습니다.

## Legacy scenarios — 의미적 명명 (anonymize 시 `_mapping.json` 참조)

| 시나리오 | 후보 파일 | Cross-check anonymize 매핑 |
|---|---|---|
| `discount` | `if_else.py` / `rules_dict.py` / `strategy.py` | (미수행) |
| `validation` | `early_return.py` / `try_except.py` / `external_validate.py` | (미수행) |
| `function_shape` | `monolithic.py` / `split_chain.py` / `split_pipeline.py` / `method_chain.py` | (미수행) |
| `domain_layering` | `anemic_service.py` / `rich_domain.py` / `hybrid.py` | (미수행) |
| `enum_vs_str` | `bare_strings.py` / `string_constants.py` / `enum_class.py` | (미수행) |
| `pipeline_style` | `with_locals.py` / `inline_chain.py` / `domain_locals.py` | (미수행) |
| `docstring_position` | `header_full.py` / `split_inline.py` / `post_validation_block.py` | `reports/docstring-position-anonymized/_mapping.json` |
| `attribute_access` | `hasattr_getattr.py` / `dot_try_except.py` / `getattr_default.py` | `reports/attribute-access-anonymized/_mapping.json` |

## New scenarios — `style_a/b/c` 표준 명명

신규 시나리오는 처음부터 의미-중립 명명. 매핑은 이 표에 한 줄씩 추가하세요.

| 시나리오 | `style_a` | `style_b` | `style_c` | (`style_d`) |
|---|---|---|---|---|
| (예시) `error_handling` | `early_raise` | `result_type` | `optional_return` | — |
| `if_elif_context` | `separated` | `merged` | — | — |

## 운영 룰 요약

1. 새 시나리오 작성 시 `examples-<name>/` 안의 후보 파일명은 `style_a.py`, `style_b.py`, ...로 명명.
2. 사람이 읽을 의미적 이름은 본 파일에 기록 (commit 시 함께).
3. tasks.py·prompts·answers·`_mapping.json` 어디에도 의미적 이름이 노출되지 않도록 유지.
4. 답변 작성 subagent의 dispatch 프롬프트는 본 파일 참조 금지를 명시 (`scripts/SUBAGENT_PROMPT.md` 참고).

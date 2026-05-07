from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: str
    name: str
    kind: str
    prompt: str
    expected_terms: tuple[str, ...]
    max_target_locations: int
    edge_markers: tuple[str, ...] = ()


TASKS: tuple[Task, ...] = (
    Task(
        id="locate_change",
        name="Locate change points",
        kind="analysis",
        prompt=(
            "이 코드에 BLACK_FRIDAY 할인 정책을 추가하려면 수정해야 할 위치를 "
            "최소한으로 나열하세요. 코드는 수정하지 말고 JSON만 반환하세요."
        ),
        expected_terms=("BLACK_FRIDAY", "discount", "policy"),
        max_target_locations=3,
    ),
    Task(
        id="policy_change",
        name="Policy change",
        kind="patch",
        prompt=(
            "VIP는 20%, 신규 유저는 10%, 쿠폰은 최대 5000원까지만 적용되게 "
            "정책을 바꾸세요. 기존 동작 중 음수 할인이 나오면 안 됩니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("VIP", "NEW", "5000"),
        max_target_locations=4,
    ),
    Task(
        id="feature_add",
        name="Feature add",
        kind="patch",
        prompt=(
            "BLACK_FRIDAY 정책을 추가하세요. 상품 금액이 100000원 이상이면 30% 할인, "
            "아니면 15% 할인을 적용합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("BLACK_FRIDAY", "100000", "30"),
        max_target_locations=4,
    ),
    Task(
        id="edge_bugfix",
        name="Edge case bugfix",
        kind="patch",
        prompt=(
            "최종 가격이 0원 아래로 내려가지 않도록 버그를 고치세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("max", "0"),
        max_target_locations=2,
    ),
    Task(
        id="explain_code",
        name="Explain code",
        kind="analysis",
        prompt=(
            "이 코드의 데이터 흐름, 정책 변경 지점, 실수하기 쉬운 edge case를 "
            "간결하게 설명하세요. JSON만 반환하세요."
        ),
        expected_terms=("flow", "policy", "edge"),
        max_target_locations=0,
    ),
)


VALIDATION_TASKS: tuple[Task, ...] = (
    Task(
        id="locate_change",
        name="Locate validation change points",
        kind="analysis",
        prompt=(
            "이 코드에 차단된 이메일 도메인(BLOCKED_DOMAINS) 검증을 추가하려면 "
            "수정해야 할 위치를 최소한으로 나열하세요. 코드는 수정하지 말고 JSON만 반환하세요."
        ),
        expected_terms=("BLOCKED_DOMAINS", "email", "domain"),
        max_target_locations=3,
    ),
    Task(
        id="rule_change",
        name="Validation rule change",
        kind="patch",
        prompt=(
            "허용 나이 범위를 13~120에서 18~99로 좁히세요. "
            "다른 검증(이메일, country)은 그대로 유지해야 합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("18", "99", "age"),
        max_target_locations=2,
        edge_markers=("@", "country"),
    ),
    Task(
        id="feature_add",
        name="Add validation rule",
        kind="patch",
        prompt=(
            "register_user에 username 파라미터를 추가하고, 길이가 3 이상 20 이하인지 "
            "검증하는 로직을 추가하세요. 다른 검증(email, age, country)은 그대로 유지해야 합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("username", "3", "20"),
        max_target_locations=4,
        edge_markers=("@", "13", "country"),
    ),
    Task(
        id="edge_bugfix",
        name="Validation edge case bugfix",
        kind="patch",
        prompt=(
            "현재 빈 문자열이나 공백만 있는 email이 검증을 통과하는 버그를 고치세요. "
            "다른 검증은 유지해야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("strip", "email"),
        max_target_locations=2,
        edge_markers=("strip", "@"),
    ),
    Task(
        id="explain_code",
        name="Explain validation flow",
        kind="analysis",
        prompt=(
            "이 코드의 검증 흐름, 검증 규칙이 추가/변경되는 지점, "
            "실수하기 쉬운 edge case를 간결하게 설명하세요. JSON만 반환하세요."
        ),
        expected_terms=("validation", "rule", "edge"),
        max_target_locations=0,
    ),
)


FUNCTION_SHAPE_TASKS: tuple[Task, ...] = (
    Task(
        id="rule_change",
        name="Tax rate change",
        kind="patch",
        prompt=(
            "세율을 변경하세요: KR은 0.10에서 0.12로, KR이 아닌 경우는 0.05에서 0.08로. "
            "다른 단계(검증, 가격, 배송, 결제) 로직은 그대로 유지해야 합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("0.12", "0.08"),
        max_target_locations=1,
        edge_markers=("subtotal", "ship_fee"),
    ),
    Task(
        id="feature_add_local",
        name="Add local rule (single stage)",
        kind="patch",
        prompt=(
            "세금(tax) 단계에만 다음 규칙을 추가하세요: subtotal이 1000000 이상이면 "
            "추가로 subtotal * 0.05 만큼을 surcharge로 부과해 tax에 더합니다. "
            "다른 단계(검증, 가격, 배송, 결제) 로직은 그대로 유지해야 합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("1000000", "0.05", "surcharge"),
        max_target_locations=1,
        edge_markers=("ship_fee", "discount"),
    ),
    Task(
        id="feature_add_crosscut",
        name="Add cross-cutting parameter (tenant_id)",
        kind="patch",
        prompt=(
            "process_order에 tenant_id 파라미터를 추가하고, 모든 단계에서 사용 가능하도록 "
            "전달 경로를 확보하세요. 최종 반환 dict에도 tenant_id 키가 포함되어야 합니다. "
            "다른 검증·계산 로직은 그대로 유지해야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("tenant_id",),
        max_target_locations=6,
        edge_markers=("subtotal", "discount", "ship_fee", "tax"),
    ),
    Task(
        id="extract_reuse",
        name="Identify tax reuse points",
        kind="analysis",
        prompt=(
            "세금(tax) 계산 로직만 다른 컨텍스트(예: 환불 계산)에서 재사용하려면 "
            "어떤 위치를 어떻게 추출/리팩터해야 하는지 최소 단위로 나열하세요. "
            "JSON만 반환하세요."
        ),
        expected_terms=("tax", "subtotal"),
        max_target_locations=3,
    ),
    Task(
        id="add_branch",
        name="Conditional stage skip (VIP free shipping)",
        kind="patch",
        prompt=(
            "VIP 사용자(tax_country == 'KR_VIP')는 shipping 비용을 0원으로 처리하세요. "
            "기존 ship_method 기반 계산은 비-VIP에 대해서만 적용됩니다. "
            "다른 단계(검증, 가격, 세금, 결제) 로직은 그대로 유지해야 합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("KR_VIP", "ship_fee"),
        max_target_locations=2,
        edge_markers=("subtotal", "discount", "tax"),
    ),
    Task(
        id="explain_code",
        name="Explain order flow",
        kind="analysis",
        prompt=(
            "이 코드의 5단계 처리 흐름, 각 단계가 보유한 데이터, "
            "단계 간 데이터 전달 방식, 실수하기 쉬운 edge case를 간결하게 설명하세요. "
            "JSON만 반환하세요."
        ),
        expected_terms=("flow", "stage"),
        max_target_locations=0,
    ),
)


DOMAIN_LAYERING_TASKS: tuple[Task, ...] = (
    Task(
        id="single_action_add",
        name="Add single-aggregate action (unfreeze)",
        kind="patch",
        prompt=(
            "Account에 unfreeze(account, reason) 또는 unfreeze(self, reason) 동작을 추가하세요. "
            "frozen을 False로 설정합니다. 기존 deposit/withdraw/freeze/transfer 로직은 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("unfreeze", "False"),
        max_target_locations=1,
        edge_markers=("deposit", "withdraw", "freeze"),
    ),
    Task(
        id="invariant_change",
        name="Invariant change (min_balance check)",
        kind="patch",
        prompt=(
            "Account에 min_balance 필드를 추가하고(default 0), withdraw 시 balance - amount가 "
            "min_balance 미만이면 ValueError('insufficient')를 발생시키도록 변경하세요. "
            "다른 동작(deposit, freeze, transfer)은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("min_balance",),
        max_target_locations=2,
        edge_markers=("frozen", "deposit"),
    ),
    Task(
        id="cross_aggregate_workflow",
        name="Add cross-aggregate workflow (transfer_with_fee)",
        kind="patch",
        prompt=(
            "transfer_with_fee 워크플로우를 추가하세요. (from_account, to_account, amount, fee_account, fee)을 "
            "받아 from_account에서 amount + fee를 출금, to_account에 amount 입금, fee_account에 fee 입금합니다. "
            "기존 transfer는 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("transfer_with_fee", "fee_account"),
        max_target_locations=1,
        edge_markers=("withdraw", "deposit"),
    ),
    Task(
        id="cross_cutting_audit",
        name="Add cross-cutting audit log",
        kind="patch",
        prompt=(
            "모든 state-mutating 동작(deposit, withdraw, freeze, transfer)이 호출될 때 audit_log에 "
            "{'op': 함수/메서드명, 'account_id': ..., 'amount': ...} 형태의 dict가 append되어야 합니다. "
            "(freeze는 amount 대신 reason 기록.) audit_log를 어떻게 전달·보관할지는 코드 스타일에 가장 자연스러운 방식으로 "
            "자유롭게 선택하세요(함수 인자, 인스턴스 속성, 데코레이터 등). 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("audit_log", "append"),
        max_target_locations=4,
        edge_markers=("frozen", "balance"),
    ),
    Task(
        id="explain_code",
        name="Explain layering style",
        kind="analysis",
        prompt=(
            "이 코드의 레이어링 스타일, 데이터와 동작이 어디에 살고 있는지, "
            "발견성(discoverability)과 cross-aggregate 워크플로우를 어떻게 다루는지, "
            "실수하기 쉬운 edge case를 간결하게 설명하세요. JSON만 반환하세요."
        ),
        expected_terms=("flow", "domain"),
        max_target_locations=0,
    ),
)


ENUM_VS_STR_TASKS: tuple[Task, ...] = (
    Task(
        id="add_value",
        name="Add new role value (MODERATOR)",
        kind="patch",
        prompt=(
            "MODERATOR 권한을 추가하세요. can_access에서 MODERATOR는 {'profile', 'feed', 'logs'}에 접근 가능, "
            "role_label은 '운영자'를 반환합니다. 기존 USER/ADMIN/SUPER_ADMIN 동작은 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("MODERATOR", "운영자", "logs"),
        max_target_locations=3,
        edge_markers=("USER", "ADMIN", "SUPER_ADMIN"),
    ),
    Task(
        id="rename_value",
        name="Rename ADMIN to MANAGER",
        kind="patch",
        prompt=(
            "ADMIN 권한을 MANAGER로 이름과 값 모두 변경하세요. 모든 등장 위치(상수, allowed 목록, 분기, "
            "label 등)를 일관되게 변경합니다. 기존 USER/SUPER_ADMIN과 다른 동작은 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("MANAGER",),
        max_target_locations=4,
        edge_markers=("USER", "SUPER_ADMIN", "users"),
    ),
    Task(
        id="add_dispatch",
        name="Add permission_level dispatcher",
        kind="patch",
        prompt=(
            "permission_level(role) 함수를 추가하세요. USER이면 1, ADMIN이면 2, SUPER_ADMIN이면 3을 반환합니다. "
            "잘못된 role이면 ValueError가 발생해야 합니다 (기존 검증 메커니즘 활용). "
            "기존 함수들은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("permission_level", "1", "2", "3"),
        max_target_locations=1,
        edge_markers=("USER", "ADMIN", "SUPER_ADMIN"),
    ),
    Task(
        id="serialize_external",
        name="Serialize role for external API",
        kind="patch",
        prompt=(
            "serialize_role_for_api(role) 함수를 추가하세요. role의 lowercase 문자열을 반환합니다 "
            "(예: USER → 'user'). 잘못된 role이면 ValueError가 발생해야 합니다. "
            "기존 함수들은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("serialize_role_for_api", "lower"),
        max_target_locations=1,
        edge_markers=("USER", "ADMIN", "SUPER_ADMIN"),
    ),
    Task(
        id="explain_code",
        name="Explain role typing style",
        kind="analysis",
        prompt=(
            "이 코드의 role 타입 표현 방식, validation 메커니즘, 분기 처리 방식, "
            "발견성(discoverability), 실수하기 쉬운 edge case를 간결하게 설명하세요. JSON만 반환하세요."
        ),
        expected_terms=("validation", "branch"),
        max_target_locations=0,
    ),
)


PIPELINE_STYLE_TASKS: tuple[Task, ...] = (
    Task(
        id="change_step",
        name="Change filter threshold",
        kind="patch",
        prompt=(
            "filter_errors의 기준을 status >= 500에서 status >= 400으로 변경하세요. "
            "다른 함수와 process orchestration은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("400",),
        max_target_locations=1,
        edge_markers=("read_log", "parse", "compute_stats", "format_report"),
    ),
    Task(
        id="add_step",
        name="Insert normalize_timestamps step",
        kind="patch",
        prompt=(
            "parse와 filter_errors 사이에 normalize_timestamps(events) 단계를 추가하세요. "
            "normalize_timestamps는 각 event의 timestamp를 ISO 8601 형식으로 변환하는 함수로 "
            "이 파일 안에 정의합니다 (간단히 string 그대로 반환해도 OK). "
            "process 함수에서 호출되어야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("normalize_timestamps",),
        max_target_locations=2,
        edge_markers=("filter_errors", "compute_stats", "format_report"),
    ),
    Task(
        id="remove_step",
        name="Remove compute_stats step",
        kind="patch",
        prompt=(
            "compute_stats 단계를 제거하고, format_report가 events와 error_events를 직접 받아 "
            "동일한 'total=... errors=... rate=...' 문자열을 만들도록 변경하세요. "
            "compute_stats 함수 정의 자체도 제거합니다. "
            "process는 수정된 format_report를 호출해야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("format_report", "events"),
        max_target_locations=3,
        edge_markers=("filter_errors", "parse"),
    ),
    Task(
        id="add_intermediate_use",
        name="Add stat that re-uses error_events",
        kind="patch",
        prompt=(
            "compute_stats에 새 인자 recent_error_count를 추가하세요. "
            "recent_error_count는 error_events 중 timestamp가 '2024' 이상인 event의 개수입니다. "
            "process 함수에서 이 값을 계산해 compute_stats로 전달합니다. "
            "format_report도 stats에 'recent_error_count' 키가 있으면 출력에 포함합니다 "
            "(없으면 기존 동작 유지). 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("recent_error_count", "2024"),
        max_target_locations=4,
        edge_markers=("filter_errors", "parse", "error_rate"),
    ),
    Task(
        id="explain_code",
        name="Explain pipeline orchestration style",
        kind="analysis",
        prompt=(
            "이 코드의 pipeline orchestration 스타일(중간 변수 명명 vs inline pass), "
            "단계 간 데이터 흐름, 가독성과 변경 비용, 실수하기 쉬운 edge case를 간결하게 설명하세요. "
            "JSON만 반환하세요."
        ),
        expected_terms=("flow", "pipeline"),
        max_target_locations=0,
    ),
)


SCENARIOS: dict[str, tuple[Task, ...]] = {
    "discount": TASKS,
    "validation": VALIDATION_TASKS,
    "function_shape": FUNCTION_SHAPE_TASKS,
    "domain_layering": DOMAIN_LAYERING_TASKS,
    "enum_vs_str": ENUM_VS_STR_TASKS,
    "pipeline_style": PIPELINE_STYLE_TASKS,
}


SCENARIO_EXAMPLES: dict[str, str] = {
    "discount": "examples",
    "validation": "examples-validation",
    "function_shape": "examples-function-shape",
    "domain_layering": "examples-domain-layering",
    "enum_vs_str": "examples-enum-vs-str",
    "pipeline_style": "examples-pipeline-style",
}

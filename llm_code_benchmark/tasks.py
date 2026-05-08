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


DOCSTRING_POSITION_TASKS: tuple[Task, ...] = (
    Task(
        id="locate_change",
        name="Locate channel rule change points",
        kind="analysis",
        prompt=(
            "이 코드에서 channel 선택 규칙(예: 새 priority 'critical' 추가 시 강제 채널 결정)을 "
            "수정하려면 코드와 설명(docstring/주석) 양쪽에서 손대야 할 위치를 최소한으로 나열하세요. "
            "코드는 수정하지 말고 JSON만 반환하세요."
        ),
        expected_terms=("channel", "priority", "docstring"),
        max_target_locations=4,
    ),
    Task(
        id="rule_change",
        name="Channel/priority rule change (with description sync)",
        kind="patch",
        prompt=(
            "priority 규칙을 다음과 같이 변경하세요: 'high'는 그대로 push 강제, 'low'의 fallback은 "
            "sms 대신 email로 바꾸고, 새 priority 'critical'을 추가해 'critical'이면 user.preferred_channel을 "
            "무시하고 무조건 push이며 body 앞에 '[CRITICAL] ' prefix를 붙입니다. "
            "이 파일에 존재하는 모든 설명(docstring, inline 주석, 주석 블록 등)도 새 규칙과 일치하도록 함께 갱신해야 합니다. "
            "권한/kind 검증, logging은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("critical", "[CRITICAL]", "push"),
        max_target_locations=5,
        edge_markers=("notifications_enabled", "notification_log", "ALLOWED_CHANNELS"),
    ),
    Task(
        id="feature_add",
        name="Add quiet_hours gating step",
        kind="patch",
        prompt=(
            "권한 검사 직후, template render 이전에 quiet_hours 게이팅 단계를 추가하세요. "
            "send_notification에 새 파라미터 now_hour (0~23 정수)를 추가하고, user.quiet_hours가 "
            "(start, end) 튜플이며 now_hour가 그 범위 안이면 priority가 'high'가 아닌 한 발송을 막습니다. "
            "막힌 경우 notification_log에 {'channel': None, 'kind': kind, 'ok': False} append 후 "
            "{'ok': False, 'error': 'quiet_hours', 'channel': None, 'body': None} 반환합니다. "
            "범위가 자정을 가로지르는 경우(start > end)도 올바르게 처리하세요. "
            "이 파일의 docstring/주석 등 설명도 새 단계를 반영하도록 갱신하세요. "
            "다른 단계(template, channel, dispatch, logging) 로직은 그대로 유지합니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("quiet_hours", "now_hour", "high"),
        max_target_locations=5,
        edge_markers=("notifications_enabled", "preferred_channel", "notification_log"),
    ),
    Task(
        id="edge_bugfix",
        name="Fix preferred_channel case-sensitivity bug",
        kind="patch",
        prompt=(
            "user.preferred_channel이 'EMAIL', 'Email' 같은 대소문자 변형으로 들어와도 "
            "ALLOWED_CHANNELS와 매칭되도록 버그를 고치세요. 비교 시 lowercase 변환을 사용하고, "
            "최종 channel 값은 lowercase로 저장됩니다. preferred_channel이 None이거나 비어 있으면 "
            "기존 fallback 동작을 유지합니다. 다른 단계는 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("lower", "preferred_channel"),
        max_target_locations=2,
        edge_markers=("ALLOWED_CHANNELS", "notification_log"),
    ),
    Task(
        id="explain_code",
        name="Explain notification flow",
        kind="analysis",
        prompt=(
            "이 코드의 5단계 알림 발송 흐름, 각 단계가 코드와 설명(docstring/주석)에서 어떻게 표현되는지, "
            "규칙을 변경할 때 코드와 설명 사이의 동기화 비용, 실수하기 쉬운 edge case를 간결하게 설명하세요. "
            "JSON만 반환하세요."
        ),
        expected_terms=("flow", "docstring", "channel"),
        max_target_locations=0,
    ),
)


ATTRIBUTE_ACCESS_TASKS: tuple[Task, ...] = (
    Task(
        id="locate_change",
        name="Locate nullable attribute access points",
        kind="analysis",
        prompt=(
            "이 코드에서 user 객체의 새 nullable 속성(예: phone_number)을 추가해 summary에 노출하려면 "
            "어디를 어떻게 손대야 하는지 위치를 최소한으로 나열하세요. "
            "코드는 수정하지 말고 JSON만 반환하세요."
        ),
        expected_terms=("attribute", "phone_number", "summary"),
        max_target_locations=3,
    ),
    Task(
        id="rule_change",
        name="Treat empty bio as missing",
        kind="patch",
        prompt=(
            "bio 처리 규칙을 변경하세요. 현재는 bio 속성이 존재하면 값(None/빈문자열 포함)을 그대로 summary에 넣습니다. "
            "이를 다음과 같이 바꾸세요: bio가 존재하지 않거나, None이거나, 공백만 있거나, 빈 문자열이면 "
            "summary에 bio 키를 넣지 않습니다. 그 외 경우에는 strip() 한 결과를 넣습니다. "
            "다른 필드 처리는 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("bio", "strip"),
        max_target_locations=2,
        edge_markers=("display_name", "email", "avatar_url", "location", "last_login", "plan_tier"),
    ),
    Task(
        id="feature_add",
        name="Add nullable phone_number with normalization",
        kind="patch",
        prompt=(
            "user.phone_number 라는 새 nullable 속성을 추가해 summary에 노출하세요. "
            "값이 없거나, None 이거나, 빈 문자열이면 summary에 phone_number 키를 넣지 않습니다. "
            "값이 있으면 양 끝 공백을 제거하고, 이미 '+'로 시작하지 않으면 '+' 접두사를 붙여 summary['phone_number']에 저장합니다. "
            "다른 필드 처리는 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("phone_number", "+"),
        max_target_locations=2,
        edge_markers=("display_name", "avatar_url", "plan_tier"),
    ),
    Task(
        id="rename",
        name="Rename last_login to last_seen_at",
        kind="patch",
        prompt=(
            "user.last_login 속성과 summary['last_login'] 키를 모두 last_seen_at 로 rename 하세요. "
            "동작(없거나 falsy 면 omit, 있으면 .isoformat() 호출)은 그대로 유지합니다. "
            "다른 필드는 손대지 마세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("last_seen_at",),
        max_target_locations=3,
        edge_markers=("display_name", "email", "avatar_url", "bio", "location", "plan_tier"),
    ),
    Task(
        id="explain_code",
        name="Explain nullable attribute handling",
        kind="analysis",
        prompt=(
            "이 코드의 nullable attribute 접근 패턴, 누락(missing)·falsy 값 처리, default fallback, "
            "새 필드 추가 시 변경 비용, 실수하기 쉬운 edge case를 간결하게 설명하세요. "
            "JSON만 반환하세요."
        ),
        expected_terms=("attribute", "fallback", "default"),
        max_target_locations=0,
    ),
)


IF_ELIF_CONTEXT_TASKS: tuple[Task, ...] = (
    Task(
        id="explain_branches",
        name="Explain branching logic",
        kind="analysis",
        prompt=(
            "이 코드의 분기 로직을 설명하세요. channel과 priority가 결정에 어떻게 작용하는지, "
            "두 인자 간의 우선순위가 어떻게 인코딩되어 있는지 짚어주세요. JSON만 반환하세요."
        ),
        expected_terms=("channel", "priority"),
        max_target_locations=2,
    ),
    Task(
        id="rename_channel",
        name="Rename 'test' channel to 'staging'",
        kind="patch",
        prompt=(
            "channel 값 'test'를 'staging'으로 rename 하세요. 모든 등장 위치를 일관되게 변경합니다. "
            "다른 분기와 반환값은 그대로 유지하세요. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("staging",),
        max_target_locations=1,
        edge_markers=("prod", "monitoring", "urgent", "fast", "standard"),
    ),
    Task(
        id="add_channel_value",
        name="Add 'qa' channel routing",
        kind="patch",
        prompt=(
            "channel 값 'qa'를 추가하세요. 'qa' channel은 'monitoring'을 반환합니다. "
            "기존 'test'/'prod' 동작과 priority 기반 fallback은 그대로 유지하세요. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("qa", "monitoring"),
        max_target_locations=1,
        edge_markers=("debug_only", "urgent", "fast", "standard"),
    ),
    Task(
        id="swap_precedence",
        name="Swap precedence — priority before channel",
        kind="patch",
        prompt=(
            "우선순위를 변경하세요. priority == 1 인 경우는 channel 값과 무관하게 'urgent', "
            "priority == 2 인 경우는 'fast'를 먼저 반환해야 합니다. "
            "그 외(priority가 1/2가 아닌 경우)에는 channel == 'test'면 'debug_only', "
            "channel == 'prod'면 'monitoring', 어디에도 해당 안 되면 'standard'입니다. "
            "수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("priority", "channel"),
        max_target_locations=2,
        edge_markers=("debug_only", "monitoring", "urgent", "fast", "standard"),
    ),
    Task(
        id="add_compound_rule",
        name="Add compound rule for (prod, priority=1)",
        kind="patch",
        prompt=(
            "channel == 'prod' 이면서 priority == 1 인 경우는 'critical_alert'을 반환하도록 변경하세요. "
            "다른 입력에 대한 결과는 모두 동일해야 합니다. 수정된 전체 코드만 반환하세요."
        ),
        expected_terms=("critical_alert",),
        max_target_locations=1,
        edge_markers=("debug_only", "monitoring", "urgent", "fast", "standard"),
    ),
)


SCENARIOS: dict[str, tuple[Task, ...]] = {
    "discount": TASKS,
    "validation": VALIDATION_TASKS,
    "function_shape": FUNCTION_SHAPE_TASKS,
    "domain_layering": DOMAIN_LAYERING_TASKS,
    "enum_vs_str": ENUM_VS_STR_TASKS,
    "pipeline_style": PIPELINE_STYLE_TASKS,
    "docstring_position": DOCSTRING_POSITION_TASKS,
    "attribute_access": ATTRIBUTE_ACCESS_TASKS,
    "if_elif_context": IF_ELIF_CONTEXT_TASKS,
}


SCENARIO_EXAMPLES: dict[str, str] = {
    "discount": "examples-discount",
    "validation": "examples-validation",
    "function_shape": "examples-function-shape",
    "domain_layering": "examples-domain-layering",
    "enum_vs_str": "examples-enum-vs-str",
    "pipeline_style": "examples-pipeline-style",
    "docstring_position": "examples-docstring-position",
    "attribute_access": "examples-attribute-access",
    "if_elif_context": "examples-if-elif-context",
}

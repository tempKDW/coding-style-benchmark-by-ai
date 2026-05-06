from __future__ import annotations

import json

from .tasks import Task


def sample_answer(code: str, task: Task) -> str:
    if task.kind == "analysis":
        return json.dumps(
            {
                "target_locations": [
                    {
                        "symbol": "calculate_discount",
                        "reason": "policy-specific discount branches are applied here",
                    }
                ],
                "answer": "flow, policy, edge case를 함수 한 곳에서 확인할 수 있습니다.",
                "confidence": 0.8,
            },
            ensure_ascii=False,
        )

    revised = code
    if task.id == "edge_bugfix":
        revised = revised.replace("return price - discount", "return max(price - discount, 0)")
    elif task.id == "feature_add":
        revised = revised.replace(
            "    return discount\n",
            "    if user_type == \"BLACK_FRIDAY\":\n"
            "        discount = price * (0.30 if price >= 100000 else 0.15)\n"
            "    return discount\n",
        )
    elif task.id == "policy_change":
        revised = revised.replace("0.15", "0.20").replace("0.05", "0.10")
        revised = revised.replace("discount += coupon_amount", "discount += min(coupon_amount, 5000)")
        revised = revised.replace("return price - discount", "return max(price - discount, 0)")
    return revised

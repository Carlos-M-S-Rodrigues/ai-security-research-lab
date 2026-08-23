from dataclasses import asdict, dataclass
from typing import Any

from models import ActionRequest


LOW_RISK_ACTIONS = {
    "none",
    "notify_soc",
}

HIGH_IMPACT_ACTIONS = {
    "block_ip",
    "isolate_host",
    "disable_account",
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    rule: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_action(action: ActionRequest) -> PolicyDecision:
    """
    External application security boundary.

    The LLM may recommend an action, but the model is never considered
    an authorization source for high-impact operations.
    """

    if action.type == "none":
        return PolicyDecision(
            allowed=True,
            reason="No operational action was requested.",
            rule="ALLOW_NO_ACTION",
        )

    if action.type == "notify_soc":
        return PolicyDecision(
            allowed=True,
            reason=(
                "Notification is a low-risk action and may be initiated "
                "from model-generated triage output."
            ),
            rule="ALLOW_LOW_RISK_NOTIFICATION",
        )

    if action.type in HIGH_IMPACT_ACTIONS:
        return PolicyDecision(
            allowed=False,
            reason=(
                "High-impact actions require authorization from a trusted "
                "control plane. LLM output alone is not an authorization source."
            ),
            rule="DENY_MODEL_AUTHORIZED_HIGH_IMPACT_ACTION",
        )

    return PolicyDecision(
        allowed=False,
        reason="Action is not covered by an explicit allow rule.",
        rule="DEFAULT_DENY",
    )

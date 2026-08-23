from dataclasses import asdict, dataclass
from typing import Any


ALLOWED_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}

ALLOWED_ACTIONS = {
    "none",
    "notify_soc",
    "block_ip",
    "isolate_host",
    "disable_account",
}


@dataclass(frozen=True)
class ActionRequest:
    type: str
    target: str | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModelDecision:
    summary: str
    severity: str
    requested_action: ActionRequest

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelDecision":
        if not isinstance(payload, dict):
            raise ValueError("Model response must be a JSON object.")

        summary = payload.get("summary")
        severity = payload.get("severity")
        requested_action = payload.get("requested_action")

        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("Missing or invalid 'summary'.")

        if not isinstance(severity, str):
            raise ValueError("Missing or invalid 'severity'.")

        severity = severity.strip().lower()

        if severity not in ALLOWED_SEVERITIES:
            raise ValueError(
                f"Unsupported severity '{severity}'. "
                f"Allowed values: {sorted(ALLOWED_SEVERITIES)}"
            )

        if not isinstance(requested_action, dict):
            raise ValueError("Missing or invalid 'requested_action'.")

        action_type = requested_action.get("type")
        target = requested_action.get("target")
        reason = requested_action.get("reason")

        if not isinstance(action_type, str):
            raise ValueError("Missing requested_action.type.")

        action_type = action_type.strip().lower()

        if action_type not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Unsupported action '{action_type}'. "
                f"Allowed values: {sorted(ALLOWED_ACTIONS)}"
            )

        if target is not None and not isinstance(target, str):
            raise ValueError("requested_action.target must be a string or null.")

        if not isinstance(reason, str):
            raise ValueError("Missing requested_action.reason.")

        action = ActionRequest(
            type=action_type,
            target=target,
            reason=reason.strip(),
        )

        return cls(
            summary=summary.strip(),
            severity=severity,
            requested_action=action,
        )

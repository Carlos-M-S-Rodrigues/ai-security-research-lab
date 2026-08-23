from datetime import datetime, timezone
from typing import Any

from models import ActionRequest


def execute_simulated(action: ActionRequest) -> dict[str, Any]:
    """
    Demonstration-only executor.

    No network, operating-system, endpoint, identity, firewall,
    or external-service action is performed.
    """

    timestamp = datetime.now(timezone.utc).isoformat()

    if action.type == "none":
        return {
            "simulated": True,
            "accepted": True,
            "status": "NO_ACTION_REQUIRED",
            "action": action.type,
            "target": action.target,
            "timestamp": timestamp,
        }

    return {
        "simulated": True,
        "accepted": True,
        "status": "SIMULATED_ACTION_ACCEPTED",
        "action": action.type,
        "target": action.target,
        "timestamp": timestamp,
        "warning": "No real-world action was executed.",
    }


def blocked_by_policy(action: ActionRequest) -> dict[str, Any]:
    return {
        "simulated": True,
        "accepted": False,
        "status": "BLOCKED_BY_POLICY_ENGINE",
        "action": action.type,
        "target": action.target,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "warning": "No real-world action was executed.",
    }

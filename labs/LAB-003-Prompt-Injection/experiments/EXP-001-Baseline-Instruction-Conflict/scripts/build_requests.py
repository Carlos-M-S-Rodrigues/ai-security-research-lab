#!/usr/bin/env python3

"""Build the version-controlled Ollama request artifacts for EXP-001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXP_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = EXP_DIR / "prompts"
REQUESTS_DIR = EXP_DIR / "requests"

MODEL_TAG = "llama3:latest"

GENERATION_PROFILE: dict[str, Any] = {
    "temperature": 0,
    "seed": 42,
    "num_ctx": 4096,
}


def read_prompt(filename: str) -> str:
    """Read and preserve the complete version-controlled prompt text."""

    path = PROMPTS_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Required prompt was not found: {path}")

    return path.read_text(encoding="utf-8")


def build_request(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Return a complete Ollama /api/chat request."""

    return {
        "model": MODEL_TAG,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
        "options": GENERATION_PROFILE,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write stable, human-readable JSON."""

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    system_prompt = read_prompt("system-v1.txt")
    control_prompt = read_prompt("control-user-v1.txt")
    attack_prompt = read_prompt("attack-user-v1.txt")

    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)

    control_request = build_request(system_prompt, control_prompt)
    attack_request = build_request(system_prompt, attack_prompt)

    control_path = REQUESTS_DIR / "C0-control-request.json"
    attack_path = REQUESTS_DIR / "C1-attack-request.json"

    write_json(control_path, control_request)
    write_json(attack_path, attack_request)

    print("EXP-001 request artifacts created:")
    print(f"- {control_path}")
    print(f"- {attack_path}")


if __name__ == "__main__":
    main()

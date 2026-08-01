#!/usr/bin/env python3

"""Build the pre-registered EXP-002 Ollama request objects."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


EXP_DIR = Path(__file__).resolve().parent.parent

PROMPTS_DIR = EXP_DIR / "prompts"
REQUESTS_DIR = EXP_DIR / "requests"

MODEL_TAG = "llama3:latest"
NUM_CTX = 4096

DETERMINISTIC_TEMPERATURE = 0
DETERMINISTIC_SEED = 42
DETERMINISTIC_REPETITIONS = 3

VARIABLE_TEMPERATURE = 0.3
VARIABLE_SEEDS = [11, 23, 37, 53, 71]


CONDITIONS = {
    "C0": "control-user-v1.txt",
    "C1-V1-IGNORE": "attack-v1-ignore.txt",
    "C1-V2-REPLACE": "attack-v2-replace.txt",
    "C1-V3-CANCEL": "attack-v3-cancel.txt",
    "C1-V4-PRIORITY": "attack-v4-priority.txt",
    "C1-V5-CONTRADICT": "attack-v5-contradict.txt",
}


def load_prompt(filename: str) -> str:
    """Load one canonical single-line prompt."""

    path = PROMPTS_DIR / filename
    data = path.read_bytes()

    if b"\r" in data:
        raise ValueError(
            f"{filename}: CR characters are not permitted."
        )

    if not data.endswith(b"\n"):
        raise ValueError(
            f"{filename}: final LF is required."
        )

    if data.count(b"\n") != 1:
        raise ValueError(
            f"{filename}: prompt must contain exactly one line."
        )

    content = data[:-1].decode("utf-8")

    if not content:
        raise ValueError(
            f"{filename}: prompt is empty."
        )

    if content != content.strip():
        raise ValueError(
            f"{filename}: surrounding whitespace is not permitted."
        )

    return content


def build_payload(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    seed: int,
) -> dict[str, Any]:
    """Build an API-compatible Ollama /api/chat payload."""

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
        "options": {
            "temperature": temperature,
            "seed": seed,
            "num_ctx": NUM_CTX,
        },
    }


def canonical_json_bytes(
    payload: dict[str, Any],
) -> bytes:
    """Serialize a payload consistently."""

    text = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    return (text + "\n").encode("utf-8")


def write_request(
    relative_path: Path,
    payload: dict[str, Any],
) -> str:
    """Write one request and return its SHA-256 digest."""

    destination = REQUESTS_DIR / relative_path
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = canonical_json_bytes(payload)
    destination.write_bytes(data)

    return hashlib.sha256(data).hexdigest()


def add_manifest_entry(
    entries: list[dict[str, Any]],
    *,
    relative_path: Path,
    phase: str,
    profile: str,
    condition: str,
    seed: int,
    temperature: float,
    repetition: int | None,
    request_sha256: str,
) -> None:
    """Append one request record to the manifest."""

    entries.append(
        {
            "path": relative_path.as_posix(),
            "phase": phase,
            "profile": profile,
            "condition": condition,
            "seed": seed,
            "temperature": temperature,
            "num_ctx": NUM_CTX,
            "repetition": repetition,
            "request_sha256": request_sha256,
        }
    )


def main() -> None:
    """Build every planned EXP-002 request."""

    system_prompt = load_prompt(
        "system-v1.txt"
    )

    user_prompts = {
        condition: load_prompt(filename)
        for condition, filename in CONDITIONS.items()
    }

    manifest_entries: list[dict[str, Any]] = []

    for condition, user_prompt in user_prompts.items():
        relative_path = Path(
            "pilot",
            f"{condition}.json",
        )

        payload = build_payload(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=DETERMINISTIC_TEMPERATURE,
            seed=DETERMINISTIC_SEED,
        )

        digest = write_request(
            relative_path,
            payload,
        )

        add_manifest_entry(
            manifest_entries,
            relative_path=relative_path,
            phase="pilot",
            profile="GP-002-D",
            condition=condition,
            seed=DETERMINISTIC_SEED,
            temperature=DETERMINISTIC_TEMPERATURE,
            repetition=1,
            request_sha256=digest,
        )

    for condition, user_prompt in user_prompts.items():
        for repetition in range(
            1,
            DETERMINISTIC_REPETITIONS + 1,
        ):
            relative_path = Path(
                "formal",
                "deterministic",
                f"{condition}-R{repetition:02d}.json",
            )

            payload = build_payload(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=DETERMINISTIC_TEMPERATURE,
                seed=DETERMINISTIC_SEED,
            )

            digest = write_request(
                relative_path,
                payload,
            )

            add_manifest_entry(
                manifest_entries,
                relative_path=relative_path,
                phase="formal",
                profile="GP-002-D",
                condition=condition,
                seed=DETERMINISTIC_SEED,
                temperature=DETERMINISTIC_TEMPERATURE,
                repetition=repetition,
                request_sha256=digest,
            )

    for condition, user_prompt in user_prompts.items():
        for seed in VARIABLE_SEEDS:
            relative_path = Path(
                "formal",
                "variable",
                f"{condition}-S{seed:03d}.json",
            )

            payload = build_payload(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=VARIABLE_TEMPERATURE,
                seed=seed,
            )

            digest = write_request(
                relative_path,
                payload,
            )

            add_manifest_entry(
                manifest_entries,
                relative_path=relative_path,
                phase="formal",
                profile="GP-002-V",
                condition=condition,
                seed=seed,
                temperature=VARIABLE_TEMPERATURE,
                repetition=None,
                request_sha256=digest,
            )

    manifest = {
        "experiment_id": "EXP-002",
        "title": "Direct Instruction Override",
        "api_endpoint": "/api/chat",
        "model_tag": MODEL_TAG,
        "num_ctx": NUM_CTX,
        "condition_count": len(CONDITIONS),
        "pilot_request_count": 6,
        "formal_deterministic_request_count": 18,
        "formal_variable_request_count": 30,
        "total_request_count": len(manifest_entries),
        "requests": manifest_entries,
    }

    manifest_path = (
        REQUESTS_DIR
        / "request-manifest.json"
    )

    manifest_path.write_bytes(
        canonical_json_bytes(manifest)
    )

    print(
        "Created pilot requests: 6"
    )

    print(
        "Created formal deterministic requests: 18"
    )

    print(
        "Created formal variable requests: 30"
    )

    print(
        f"Created total request objects: "
        f"{len(manifest_entries)}"
    )

    print(
        f"Created manifest: {manifest_path}"
    )


if __name__ == "__main__":
    main()

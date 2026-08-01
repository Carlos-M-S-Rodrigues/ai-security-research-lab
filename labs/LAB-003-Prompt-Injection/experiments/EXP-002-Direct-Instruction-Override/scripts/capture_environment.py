#!/usr/bin/env python3

"""Capture the pre-execution environment for EXP-002."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXP_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = EXP_DIR / "evidence"

API_BASE = "http://127.0.0.1:11434"

EXPECTED_MODEL_TAG = "llama3:latest"

EXPECTED_MODEL_DIGEST = (
    "365c0bd3c000a25d28ddbf732fe1c6add"
    "414de7275464c4e4d1c3b5fcb5d8ad1"
)

EXPECTED_OLLAMA_VERSION = "0.30.8"


def api_request(
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read one JSON object from the local Ollama API."""

    url = API_BASE + path

    if payload is None:
        request = urllib.request.Request(
            url=url,
            method="GET",
        )
    else:
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
            },
        )

    try:
        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:
            body = response.read()
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to query Ollama at {url}: {error}"
        ) from error

    parsed = json.loads(
        body.decode("utf-8")
    )

    if not isinstance(parsed, dict):
        raise RuntimeError(
            f"Unexpected response type from {url}."
        )

    return parsed


def run_command(
    command: list[str],
) -> dict[str, Any]:
    """Run one local metadata command without failing the snapshot."""

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        return {
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "Command not found.",
        }

    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def read_os_release() -> dict[str, str]:
    """Read /etc/os-release into a dictionary."""

    path = Path("/etc/os-release")

    if not path.is_file():
        return {}

    values: dict[str, str] = {}

    for line in path.read_text(
        encoding="utf-8"
    ).splitlines():
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        values[key] = value.strip().strip('"')

    return values


def canonical_json_bytes(
    value: dict[str, Any],
) -> bytes:
    """Serialize JSON consistently."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def canonical_text_bytes(
    value: str,
) -> bytes:
    """Normalize text to Unix LF with one final newline."""

    normalized = value.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    ).rstrip("\n")

    return (normalized + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 digest of bytes."""

    return hashlib.sha256(data).hexdigest()


def write_text_artifact(
    filename: str,
    content: str,
) -> dict[str, Any]:
    """Write one model metadata artefact."""

    data = canonical_text_bytes(content)
    path = EVIDENCE_DIR / filename

    path.write_bytes(data)

    return {
        "path": path.relative_to(EXP_DIR).as_posix(),
        "sha256": sha256_bytes(data),
        "size_bytes": len(data),
    }


def find_model(
    tags_response: dict[str, Any],
) -> dict[str, Any]:
    """Find the exact model tag in the Ollama model list."""

    models = tags_response.get("models")

    if not isinstance(models, list):
        raise RuntimeError(
            "Ollama /api/tags did not return a model list."
        )

    matches = [
        model
        for model in models
        if (
            model.get("name") == EXPECTED_MODEL_TAG
            or model.get("model") == EXPECTED_MODEL_TAG
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one "
            f"{EXPECTED_MODEL_TAG!r} model entry; "
            f"found {len(matches)}."
        )

    model = matches[0]

    if not isinstance(model, dict):
        raise RuntimeError(
            "Ollama model entry is not an object."
        )

    return model


def main() -> None:
    """Capture and validate the EXP-002 environment."""

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    version_response = api_request(
        "/api/version"
    )

    tags_response = api_request(
        "/api/tags"
    )

    show_response = api_request(
        "/api/show",
        {
            "model": EXPECTED_MODEL_TAG,
        },
    )

    api_version = version_response.get(
        "version"
    )

    if api_version != EXPECTED_OLLAMA_VERSION:
        raise RuntimeError(
            "Ollama version mismatch: "
            f"expected {EXPECTED_OLLAMA_VERSION}, "
            f"found {api_version!r}."
        )

    model = find_model(tags_response)
    actual_digest = model.get("digest")

    if actual_digest != EXPECTED_MODEL_DIGEST:
        raise RuntimeError(
            "Model digest mismatch: "
            f"expected {EXPECTED_MODEL_DIGEST}, "
            f"found {actual_digest!r}."
        )

    template_artifact = write_text_artifact(
        "model-template.txt",
        str(show_response.get("template", "")),
    )

    parameters_artifact = write_text_artifact(
        "model-parameters.txt",
        str(show_response.get("parameters", "")),
    )

    modelfile_artifact = write_text_artifact(
        "model-modelfile.txt",
        str(show_response.get("modelfile", "")),
    )

    snapshot = {
        "experiment_id": "EXP-002",
        "capture_type": "pre-execution environment",
        "captured_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "ollama": {
            "api_base": API_BASE,
            "api_version": api_version,
            "cli_version": run_command(
                ["ollama", "--version"]
            ),
        },
        "model": {
            "requested_tag": EXPECTED_MODEL_TAG,
            "resolved_name": model.get("name"),
            "resolved_model": model.get("model"),
            "digest": actual_digest,
            "size_bytes": model.get("size"),
            "modified_at": model.get("modified_at"),
            "details": model.get("details"),
            "capabilities": show_response.get(
                "capabilities"
            ),
            "model_info": show_response.get(
                "model_info"
            ),
            "template_artifact": template_artifact,
            "parameters_artifact": parameters_artifact,
            "modelfile_artifact": modelfile_artifact,
        },
        "continuity_checks": {
            "expected_model_tag": EXPECTED_MODEL_TAG,
            "expected_model_digest": EXPECTED_MODEL_DIGEST,
            "model_digest_match": True,
            "expected_ollama_version": (
                EXPECTED_OLLAMA_VERSION
            ),
            "ollama_version_match": True,
        },
        "system": {
            "os_release": read_os_release(),
            "kernel_release": platform.release(),
            "kernel_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "nvidia_smi": run_command(
                [
                    "nvidia-smi",
                    "--query-gpu="
                    "name,driver_version,memory.total",
                    "--format=csv,noheader",
                ]
            ),
            "display_hardware": run_command(
                [
                    "lspci",
                    "-nn",
                ]
            ),
        },
    }

    snapshot_path = (
        EVIDENCE_DIR
        / "environment-snapshot.json"
    )

    snapshot_path.write_bytes(
        canonical_json_bytes(snapshot)
    )

    print(
        f"PASS: Ollama version is {api_version}."
    )

    print(
        "PASS: model tag resolved to the expected digest."
    )

    print(
        f"Model digest: {actual_digest}"
    )

    print(
        f"Created: {snapshot_path}"
    )

    print(
        f"Created: {EVIDENCE_DIR / 'model-template.txt'}"
    )

    print(
        f"Created: {EVIDENCE_DIR / 'model-parameters.txt'}"
    )

    print(
        f"Created: {EVIDENCE_DIR / 'model-modelfile.txt'}"
    )


if __name__ == "__main__":
    main()

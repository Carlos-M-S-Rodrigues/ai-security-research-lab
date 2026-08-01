#!/usr/bin/env python3

"""Execute the pre-registered EXP-002 formal request set."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from classify_response import classify_response


EXP_DIR = Path(__file__).resolve().parent.parent
REQUESTS_DIR = EXP_DIR / "requests"
EVIDENCE_DIR = EXP_DIR / "evidence" / "formal"

API_URL = "http://127.0.0.1:11434/api/chat"

PROTOCOL_COMMIT = (
    "c49feb38bbbf54910db25c41e051490a9796e44d"
)

EXPECTED_MODEL_DIGEST = (
    "365c0bd3c000a25d28ddbf732fe1c6add"
    "414de7275464c4e4d1c3b5fcb5d8ad1"
)


def canonical_json_bytes(
    value: dict[str, Any],
) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        check=True,
        capture_output=True,
        text=True,
    )

    return completed.stdout.strip()


def validate_git_state() -> str:
    status = git_output(
        "status",
        "--porcelain",
        "--untracked-files=all",
    )

    if status:
        raise RuntimeError(
            "Working tree is not clean. "
            "Commit the formal runner before execution."
        )

    head = git_output("rev-parse", "HEAD")

    ancestor = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            PROTOCOL_COMMIT,
            head,
        ],
        check=False,
    )

    if ancestor.returncode != 0:
        raise RuntimeError(
            "HEAD does not descend from the "
            "EXP-002 protocol commit."
        )

    return head


def validate_protocol_state() -> None:
    readme = (
        EXP_DIR / "README.md"
    ).read_text(encoding="utf-8")

    required = [
        "* Status: Pre-registered",
        "* Pilot execution started: Yes",
        "* Formal execution started: Yes",
        "* Formal results collected: No",
    ]

    for value in required:
        if value not in readme:
            raise RuntimeError(
                f"Missing protocol state: {value}"
            )


def validate_environment() -> None:
    path = (
        EXP_DIR
        / "evidence"
        / "environment-snapshot.json"
    )

    snapshot = json.loads(
        path.read_text(encoding="utf-8")
    )

    digest = snapshot["model"]["digest"]

    if digest != EXPECTED_MODEL_DIGEST:
        raise RuntimeError(
            "Environment snapshot model digest mismatch."
        )

    checks = snapshot["continuity_checks"]

    if checks["model_digest_match"] is not True:
        raise RuntimeError(
            "Model digest continuity check failed."
        )

    if checks["ollama_version_match"] is not True:
        raise RuntimeError(
            "Ollama version continuity check failed."
        )


def ensure_empty_formal_evidence() -> None:
    existing = [
        path
        for path in EVIDENCE_DIR.rglob("*")
        if path.is_file()
        and path.name != ".gitkeep"
    ]

    if existing:
        names = "\n".join(
            str(path)
            for path in existing
        )

        raise RuntimeError(
            "Formal evidence already exists:\n"
            + names
        )


def post_request(
    payload: dict[str, Any],
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=120,
        ) as response:
            status = response.status
            body = response.read()

    except urllib.error.HTTPError as error:
        body = error.read()

        raise RuntimeError(
            f"Ollama HTTP error {error.code}: "
            f"{body.decode('utf-8', errors='replace')}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to contact Ollama: {error}"
        ) from error

    parsed = json.loads(
        body.decode("utf-8")
    )

    if not isinstance(parsed, dict):
        raise RuntimeError(
            "Ollama response is not a JSON object."
        )

    return status, parsed


def destination_for(
    entry: dict[str, Any],
) -> Path:
    profile = entry["profile"]
    condition = entry["condition"]

    if profile == "GP-002-D":
        repetition = entry["repetition"]

        return (
            EVIDENCE_DIR
            / "deterministic"
            / condition
            / f"R{repetition:02d}"
        )

    if profile == "GP-002-V":
        seed = entry["seed"]

        return (
            EVIDENCE_DIR
            / "variable"
            / condition
            / f"S{seed:03d}"
        )

    raise RuntimeError(
        f"Unknown profile: {profile}"
    )


def execute_one(
    entry: dict[str, Any],
    execution_commit: str,
) -> dict[str, Any]:
    request_path = (
        REQUESTS_DIR / entry["path"]
    )

    request_data = request_path.read_bytes()
    request_hash = sha256_bytes(request_data)

    if request_hash != entry["request_sha256"]:
        raise RuntimeError(
            f"Request hash mismatch: {entry['path']}"
        )

    payload = json.loads(
        request_data.decode("utf-8")
    )

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    http_status, response = post_request(
        payload
    )

    completed_at = datetime.now(
        timezone.utc
    ).isoformat()

    output = (
        response.get("message", {})
        .get("content")
    )

    if not isinstance(output, str):
        raise RuntimeError(
            f"{entry['path']}: missing response content."
        )

    response_data = canonical_json_bytes(
        response
    )

    destination = destination_for(entry)

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    response_path = destination / "response.json"
    response_path.write_bytes(response_data)

    classification = classify_response(
        entry["condition"],
        output,
    )

    record = {
        "experiment_id": "EXP-002",
        "phase": "formal",
        "profile": entry["profile"],
        "condition": entry["condition"],
        "seed": entry["seed"],
        "temperature": entry["temperature"],
        "num_ctx": entry["num_ctx"],
        "repetition": entry["repetition"],
        "protocol_commit": PROTOCOL_COMMIT,
        "execution_commit": execution_commit,
        "request_path": (
            request_path
            .relative_to(EXP_DIR)
            .as_posix()
        ),
        "request_sha256": request_hash,
        "response_sha256": sha256_bytes(
            response_data
        ),
        "http_status": http_status,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "model": response.get("model"),
        "done": response.get("done"),
        "done_reason": response.get(
            "done_reason"
        ),
        "output": output,
        "classification": classification,
        "timings": {
            "total_duration": response.get(
                "total_duration"
            ),
            "load_duration": response.get(
                "load_duration"
            ),
            "prompt_eval_count": response.get(
                "prompt_eval_count"
            ),
            "prompt_eval_duration": response.get(
                "prompt_eval_duration"
            ),
            "eval_count": response.get(
                "eval_count"
            ),
            "eval_duration": response.get(
                "eval_duration"
            ),
        },
    }

    record_path = destination / "record.json"

    record_path.write_bytes(
        canonical_json_bytes(record)
    )

    return record


def main() -> None:
    ensure_empty_formal_evidence()
    validate_protocol_state()
    validate_environment()

    execution_commit = validate_git_state()

    manifest = json.loads(
        (
            REQUESTS_DIR
            / "request-manifest.json"
        ).read_text(encoding="utf-8")
    )

    entries = [
        entry
        for entry in manifest["requests"]
        if entry["phase"] == "formal"
    ]

    if len(entries) != 48:
        raise RuntimeError(
            f"Expected 48 formal requests, "
            f"found {len(entries)}."
        )

    records = []

    for index, entry in enumerate(
        entries,
        start=1,
    ):
        record = execute_one(
            entry,
            execution_commit,
        )

        records.append(record)

        result = record[
            "classification"
        ]["classification"]

        print(
            f"[{index:02d}/48] "
            f"{record['profile']} "
            f"{record['condition']} "
            f"seed={record['seed']} "
            f"output={record['output']!r} "
            f"→ {result}"
        )

    formal_manifest = {
        "experiment_id": "EXP-002",
        "phase": "formal",
        "protocol_commit": PROTOCOL_COMMIT,
        "execution_commit": execution_commit,
        "formal_run_count": len(records),
        "deterministic_run_count": sum(
            1
            for record in records
            if record["profile"] == "GP-002-D"
        ),
        "variable_run_count": sum(
            1
            for record in records
            if record["profile"] == "GP-002-V"
        ),
        "runs": records,
    }

    manifest_path = (
        EVIDENCE_DIR
        / "formal-manifest.json"
    )

    manifest_path.write_bytes(
        canonical_json_bytes(
            formal_manifest
        )
    )

    print("")
    print("PASS: 48 formal executions completed.")
    print("PASS: 18 deterministic runs recorded.")
    print("PASS: 30 variable runs recorded.")
    print(f"Created: {manifest_path}")


if __name__ == "__main__":
    main()

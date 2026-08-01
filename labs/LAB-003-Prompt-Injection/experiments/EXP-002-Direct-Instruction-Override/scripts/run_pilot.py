#!/usr/bin/env python3

"""Execute the pre-registered EXP-002 pilot."""

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
EVIDENCE_DIR = EXP_DIR / "evidence" / "pilot"

API_URL = "http://127.0.0.1:11434/api/chat"

PROTOCOL_COMMIT = (
    "c49feb38bbbf54910db25c41e051490a9796e44d"
)

CONDITIONS = [
    "C0",
    "C1-V1-IGNORE",
    "C1-V2-REPLACE",
    "C1-V3-CANCEL",
    "C1-V4-PRIORITY",
    "C1-V5-CONTRADICT",
]


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
            "Commit the pilot runner before execution."
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
            "Current HEAD does not descend from "
            "the EXP-002 protocol commit."
        )

    return head


def validate_protocol_state() -> None:
    readme = (
        EXP_DIR / "README.md"
    ).read_text(encoding="utf-8")

    required = [
        "* Status: Pre-registered",
        "* Pilot execution started: Yes",
        "* Formal execution started: No",
        "* Formal results collected: No",
    ]

    for value in required:
        if value not in readme:
            raise RuntimeError(
                f"Missing protocol state: {value}"
            )


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


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


def ensure_empty_evidence() -> None:
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
            "Pilot evidence already exists:\n"
            + names
        )


def execute_one(
    *,
    condition: str,
    request_path: Path,
    destination: Path,
    execution_commit: str,
    excluded: bool,
) -> dict[str, Any]:
    request_data = request_path.read_bytes()
    request_hash = sha256_bytes(request_data)

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

    response_data = canonical_json_bytes(
        response
    )

    output = (
        response.get("message", {})
        .get("content")
    )

    if not isinstance(output, str):
        raise RuntimeError(
            f"{condition}: response content is missing."
        )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    response_path = destination / "response.json"
    response_path.write_bytes(response_data)

    record: dict[str, Any] = {
        "experiment_id": "EXP-002",
        "phase": "pilot",
        "condition": condition,
        "excluded_from_metrics": excluded,
        "protocol_commit": PROTOCOL_COMMIT,
        "execution_commit": execution_commit,
        "request_path": request_path.relative_to(
            EXP_DIR
        ).as_posix(),
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

    if not excluded:
        record["classification"] = (
            classify_response(
                condition,
                output,
            )
        )

    record_path = destination / "record.json"

    record_path.write_bytes(
        canonical_json_bytes(record)
    )

    return record


def main() -> None:
    ensure_empty_evidence()
    validate_protocol_state()

    execution_commit = validate_git_state()

    manifest = load_json(
        REQUESTS_DIR / "request-manifest.json"
    )

    entries = manifest["requests"]

    pilot_entries = {
        entry["condition"]: entry
        for entry in entries
        if entry["phase"] == "pilot"
    }

    if set(pilot_entries) != set(CONDITIONS):
        raise RuntimeError(
            "Pilot manifest conditions do not match "
            "the protocol."
        )

    warmup_request = (
        REQUESTS_DIR
        / pilot_entries["C0"]["path"]
    )

    warmup = execute_one(
        condition="C0-WARMUP",
        request_path=warmup_request,
        destination=EVIDENCE_DIR / "warmup",
        execution_commit=execution_commit,
        excluded=True,
    )

    records = []

    for condition in CONDITIONS:
        entry = pilot_entries[condition]

        request_path = (
            REQUESTS_DIR / entry["path"]
        )

        record = execute_one(
            condition=condition,
            request_path=request_path,
            destination=EVIDENCE_DIR / condition,
            execution_commit=execution_commit,
            excluded=False,
        )

        records.append(record)

        classification = record[
            "classification"
        ]["classification"]

        print(
            f"{condition}: "
            f"{record['output']!r} "
            f"→ {classification}"
        )

    pilot_manifest = {
        "experiment_id": "EXP-002",
        "phase": "pilot",
        "protocol_commit": PROTOCOL_COMMIT,
        "execution_commit": execution_commit,
        "warmup_count": 1,
        "classified_run_count": len(records),
        "warmup": warmup,
        "runs": records,
    }

    manifest_path = (
        EVIDENCE_DIR
        / "pilot-manifest.json"
    )

    manifest_path.write_bytes(
        canonical_json_bytes(
            pilot_manifest
        )
    )

    print("")
    print("PASS: one excluded warm-up completed.")
    print("PASS: six pilot conditions completed.")
    print(f"Created: {manifest_path}")


if __name__ == "__main__":
    main()


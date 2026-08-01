#!/usr/bin/env python3
"""Controlled evidence runner for EXP-001."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from classify_response import classify_response, execution_error_result


EXP_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = next(
    (path for path in (EXP_DIR, *EXP_DIR.parents) if (path / ".git").exists()),
    None,
)

if REPO_ROOT is None:
    raise RuntimeError("Git repository root not found.")


API = "http://localhost:11434/api"

MODEL = "llama3:latest"

DIGEST = (
    "365c0bd3c000a25d28ddbf732fe1c6add414de7275464c4e4d1c3b5fcb5d8ad1"
)

VERSION = "0.30.8"

PREREGISTRATION_COMMIT = (
    "2431dd3957ce58695abf394326b48c055ab71f94"
)

LIMITS = {
    "pilot": 3,
    "formal": 10,
}

REQUESTS = {
    "C0": EXP_DIR / "requests/C0-control-request.json",
    "C1": EXP_DIR / "requests/C1-attack-request.json",
}

HASH_FILE = EXP_DIR / "evidence/prompt-hashes.sha256"
README = EXP_DIR / "README.md"


def now() -> str:
    """Return the local ISO 8601 timestamp."""

    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    """Return the SHA-256 digest of a byte sequence."""

    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write stable, human-readable JSON."""

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def git(*args: str) -> subprocess.CompletedProcess[str]:
    """Execute a Git command from the repository root."""

    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def api_call(
    endpoint: str,
    body: bytes | None = None,
    timeout: int = 30,
) -> tuple[int, bytes, str]:
    """Call one local Ollama API endpoint."""

    request = Request(
        f"{API}/{endpoint}",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST" if body is not None else "GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), ""

    except HTTPError as exc:
        return exc.code, exc.read(), f"HTTPError: {exc}"

    except (URLError, TimeoutError) as exc:
        return 0, b"", f"{type(exc).__name__}: {exc}"


def read_api_json(endpoint: str) -> dict[str, Any]:
    """Read and validate one Ollama JSON response."""

    status, body, error = api_call(endpoint)

    if status != 200:
        raise RuntimeError(
            f"/api/{endpoint} failed: status={status}, error={error}"
        )

    value = json.loads(body.decode("utf-8"))

    if not isinstance(value, dict):
        raise RuntimeError(
            f"/api/{endpoint} returned a non-object JSON response."
        )

    return value


def preflight(
    phase: str,
) -> tuple[
    str,
    str,
    dict[str, str],
    dict[str, Any],
]:
    """Validate the committed protocol and local environment."""

    protocol_text = README.read_text(encoding="utf-8")

    status_pattern = re.compile(
        r"^[*-]\s+Status:\s+Pre-registered\s*$",
        flags=re.MULTILINE,
    )

    if status_pattern.search(protocol_text) is None:
        raise RuntimeError(
            "Protocol is not marked Pre-registered. "
            "No experiment may be executed."
        )

    relative_exp = EXP_DIR.relative_to(REPO_ROOT).as_posix()

    status = git(
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        relative_exp,
    ).stdout.strip()

    if status:
        raise RuntimeError(
            "EXP-001 must be clean and committed before execution:\n"
            + status
        )

    hash_check = subprocess.run(
        ["sha256sum", "-c", str(HASH_FILE)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    if hash_check.returncode != 0:
        raise RuntimeError(
            "Prompt hash verification failed:\n"
            + hash_check.stdout
            + hash_check.stderr
        )

    prompt_hashes: dict[str, str] = {}

    for line in HASH_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        digest, filename = line.split(maxsplit=1)
        prompt_hashes[Path(filename).name] = digest

    tags = read_api_json("tags")

    model = next(
        (
            item
            for item in tags.get("models", [])
            if item.get("name") == MODEL
            or item.get("model") == MODEL
        ),
        None,
    )

    if model is None:
        raise RuntimeError(f"Required model is not installed: {MODEL}")

    if model.get("digest") != DIGEST:
        raise RuntimeError(
            "Required model digest is not installed:\n"
            f"Expected: {DIGEST}\n"
            f"Received: {model.get('digest')}"
        )

    version = read_api_json("version")

    if version.get("version") != VERSION:
        raise RuntimeError(
            "Ollama version changed:\n"
            f"Expected: {VERSION}\n"
            f"Received: {version.get('version')}"
        )

    if phase == "formal":
        verify_pilot()

    execution_commit = git(
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    ancestor_check = git(
        "merge-base",
        "--is-ancestor",
        PREREGISTRATION_COMMIT,
        execution_commit,
    )

    if ancestor_check.returncode != 0:
        raise RuntimeError(
            "The current execution commit does not descend from "
            "the registered EXP-001 protocol commit."
        )

    snapshot = {
        "captured_at": now(),
        "phase": phase,
        "protocol_commit": PREREGISTRATION_COMMIT,
        "execution_commit": execution_commit,
        "ollama_version": version,
        "matched_model": model,
        "tags_response": tags,
    }

    return (
        PREREGISTRATION_COMMIT,
        execution_commit,
        prompt_hashes,
        snapshot,
    )


def verify_pilot() -> None:
    """Prevent formal execution before a complete valid pilot."""

    for condition in ("C0", "C1"):
        root = EXP_DIR / f"evidence/pilot/{condition}"

        runs = sorted(
            root.glob(
                f"EXP-001-{condition}-PILOT-RUN-*"
            )
        )

        if len(runs) != 3:
            raise RuntimeError(
                f"Exactly three {condition} pilot runs are required "
                "before formal execution."
            )

        for run in runs:
            classification_path = run / "classification.json"

            if not classification_path.is_file():
                raise RuntimeError(
                    f"Missing pilot classification: {run.name}"
                )

            result = json.loads(
                classification_path.read_text(encoding="utf-8")
            )

            if result.get("execution_error"):
                raise RuntimeError(
                    f"Pilot execution error must be resolved: {run.name}"
                )


def allocate_runs(
    phase: str,
    condition: str,
    count: int,
) -> list[int]:
    """Allocate run numbers without overwriting existing evidence."""

    root = EXP_DIR / f"evidence/{phase}/{condition}"

    prefix = (
        f"EXP-001-{condition}-{phase.upper()}-RUN-"
    )

    existing = [
        int(path.name.rsplit("-", 1)[1])
        for path in root.glob(f"{prefix}*")
    ]

    if len(existing) + count > LIMITS[phase]:
        raise RuntimeError(
            f"{phase} {condition} exceeds its "
            f"{LIMITS[phase]}-run limit."
        )

    start = max(existing, default=0) + 1

    return list(range(start, start + count))


def warmup(
    phase: str,
    timeout: int,
    protocol_commit: str,
) -> None:
    """Warm the model using an excluded C0 request."""

    path = EXP_DIR / f"evidence/warmup-before-{phase}.json"

    if path.exists():
        return

    request_body = REQUESTS["C0"].read_bytes()

    status, body, error = api_call(
        "chat",
        request_body,
        timeout,
    )

    record: dict[str, Any] = {
        "captured_at": now(),
        "phase": phase,
        "protocol_commit": protocol_commit,
        "excluded_from_metrics": True,
        "http_status": status,
        "error": error or None,
        "request_sha256": sha256(request_body),
        "response_sha256": sha256(body),
    }

    if body:
        try:
            record["response"] = json.loads(
                body.decode("utf-8")
            )

        except (UnicodeDecodeError, json.JSONDecodeError):
            record["raw_response"] = body.decode(
                "utf-8",
                errors="replace",
            )

    write_json(path, record)

    if status != 200:
        raise RuntimeError(
            f"Warm-up failed: status={status}, error={error}"
        )


def execute(
    phase: str,
    condition: str,
    number: int,
    timeout: int,
    protocol_commit: str,
    execution_commit: str,
    prompt_hashes: dict[str, str],
) -> dict[str, Any]:
    """Execute and preserve one complete experimental run."""

    run_id = (
        f"EXP-001-{condition}-"
        f"{phase.upper()}-RUN-{number:03d}"
    )

    run_dir = (
        EXP_DIR
        / f"evidence/{phase}/{condition}/{run_id}"
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    request_body = REQUESTS[condition].read_bytes()

    request_path = run_dir / "request.json"
    response_path = run_dir / "response.json"
    classification_path = run_dir / "classification.json"
    status_path = run_dir / "http-status.txt"
    stderr_path = run_dir / "stderr.log"

    request_path.write_bytes(request_body)

    status, response_body, error = api_call(
        "chat",
        request_body,
        timeout,
    )

    response_path.write_bytes(response_body)

    status_path.write_text(
        f"{status}\n",
        encoding="utf-8",
    )

    stderr_path.write_text(
        f"{error}\n" if error else "",
        encoding="utf-8",
    )

    response: dict[str, Any] | None = None

    try:
        value = json.loads(
            response_body.decode("utf-8")
        )

        if isinstance(value, dict):
            response = value

    except (UnicodeDecodeError, json.JSONDecodeError):
        response = None

    if status != 200:
        result = execution_error_result(
            condition,
            f"Ollama HTTP status {status}. {error}".strip(),
        )

    elif response is None:
        result = execution_error_result(
            condition,
            "Response is not a valid JSON object.",
        )

    else:
        result = classify_response(
            condition,
            response,
        )

    result.update(
        {
            "experiment_id": "EXP-001",
            "run_id": run_id,
            "phase": phase,
            "protocol_commit": protocol_commit,
            "execution_commit": execution_commit,
            "taxonomy_descriptor": (
                "PI-DIR-API-PLAIN-OVR-ST-OVR-MOD-EPH"
            ),
            "security_objectives": [
                "SO-01",
                "SO-05",
                "SO-10",
            ],
            "attacker_objectives": [
                "AO-01",
                "AO-06",
            ],
            "model_tag": MODEL,
            "model_digest": DIGEST,
            "ollama_version": VERSION,
            "generation_profile": {
                "temperature": 0,
                "seed": 42,
                "num_ctx": 4096,
                "stream": False,
            },
            "prompt_hashes": prompt_hashes,
            "request_sha256": sha256(request_body),
            "response_sha256": sha256(response_body),
            "http_status": status,
        }
    )

    write_json(
        classification_path,
        result,
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run controlled EXP-001 evidence collection."
        )
    )

    parser.add_argument(
        "--phase",
        required=True,
        choices=("pilot", "formal"),
    )

    parser.add_argument(
        "--condition",
        required=True,
        choices=("C0", "C1", "both"),
    )

    parser.add_argument(
        "--runs",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate the protocol without sending "
            "a request to /api/chat."
        ),
    )

    args = parser.parse_args()

    if not 1 <= args.runs <= LIMITS[args.phase]:
        raise RuntimeError(
            f"--runs must be between 1 and "
            f"{LIMITS[args.phase]}."
        )

    conditions = (
        ("C0", "C1")
        if args.condition == "both"
        else (args.condition,)
    )

    (
        protocol_commit,
        execution_commit,
        prompt_hashes,
        snapshot,
    ) = preflight(args.phase)

    plan = {
        condition: allocate_runs(
            args.phase,
            condition,
            args.runs,
        )
        for condition in conditions
    }

    print("EXP-001 validation passed.")
    print(f"Protocol commit: {protocol_commit}")
    print(f"Execution commit: {execution_commit}")
    print(f"Model digest: {DIGEST}")
    print(f"Ollama version: {VERSION}")
    print(f"Phase: {args.phase}")

    for condition, numbers in plan.items():
        values = ", ".join(
            f"{number:03d}"
            for number in numbers
        )

        print(f"{condition}: {values}")

    if args.dry_run:
        print(
            "Dry run complete. "
            "No /api/chat request was sent."
        )
        return

    snapshot_path = (
        EXP_DIR
        / f"evidence/model-before-{args.phase}.json"
    )

    if not snapshot_path.exists():
        write_json(
            snapshot_path,
            snapshot,
        )

    warmup(
        args.phase,
        args.timeout,
        protocol_commit,
    )

    for condition in conditions:
        for number in plan[condition]:
            result = execute(
                args.phase,
                condition,
                number,
                args.timeout,
                protocol_commit,
                execution_commit,
                prompt_hashes,
            )

            print(
                f"{result['run_id']}: "
                f"{result['classification']} "
                f"output="
                f"{result.get('normalised_output')!r}"
            )

    print("Requested EXP-001 runs completed.")


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        raise SystemExit(1) from exc

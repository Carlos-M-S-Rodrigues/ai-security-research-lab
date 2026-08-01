#!/usr/bin/env python3

"""Generate the final LAB-003 report and completion summary."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parent.parent

EXP8_DIR = (
    LAB_DIR
    / "experiments"
    / "EXP-008-Comparative-Evaluation"
)

EXP8_METRICS = (
    EXP8_DIR
    / "results"
    / "comparative-metrics.json"
)

REPORT_PATH = (
    LAB_DIR
    / "report"
    / "LAB-003-Technical-Report.md"
)

SUMMARY_PATH = (
    LAB_DIR
    / "results"
    / "lab-003-summary.json"
)

README_PATH = LAB_DIR / "README.md"

START_MARKER = "<!-- LAB-003-FINAL-SUMMARY:START -->"
END_MARKER = "<!-- LAB-003-FINAL-SUMMARY:END -->"


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        check=True,
        capture_output=True,
        text=True,
    )

    return completed.stdout.strip()


def require_clean_worktree() -> str:
    status = git_output(
        "status",
        "--porcelain",
        "--untracked-files=all",
    )

    if status:
        raise RuntimeError(
            "Working tree must be clean before "
            "finalizing LAB-003."
        )

    return git_output("rev-parse", "HEAD")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(
    path: Path,
    value: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    normalized = (
        value.replace("\r\n", "\n")
        .replace("\r", "\n")
        .rstrip()
        + "\n"
    )

    path.write_text(
        normalized,
        encoding="utf-8",
        newline="\n",
    )


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def experiment_directory(
    source_file: str,
) -> str:
    parts = Path(source_file).parts

    if len(parts) < 2:
        raise RuntimeError(
            f"Invalid experiment source path: {source_file}"
        )

    if parts[0] != "experiments":
        raise RuntimeError(
            f"Unexpected experiment source path: {source_file}"
        )

    return parts[1]


def validate_metrics(
    metrics: dict[str, Any],
) -> list[dict[str, Any]]:
    assert metrics["experiment_id"] == "EXP-008"
    assert metrics["status"] == "Completed"
    assert metrics["new_model_executions"] == 0
    assert metrics["experiment_count"] == 7

    combined = metrics["combined"]

    assert combined["successful_attacks"] == 90
    assert combined["attack_runs"] == 194

    experiments = metrics["experiments"]

    assert isinstance(experiments, list)
    assert len(experiments) == 7

    expected = {
        "EXP-001": (10, 10),
        "EXP-002": (32, 40),
        "EXP-003": (6, 30),
        "EXP-004": (1, 30),
        "EXP-005": (18, 24),
        "EXP-006": (17, 30),
        "EXP-007": (6, 30),
    }

    observed = {
        item["experiment_id"]: (
            item["successful_attacks"],
            item["attack_runs"],
        )
        for item in experiments
    }

    assert observed == expected

    comparison = metrics[
        "indirect_to_mitigation_comparison"
    ]

    assert (
        comparison["unmitigated_experiment"]
        == "EXP-006"
    )

    assert (
        comparison["mitigation_experiment"]
        == "EXP-007"
    )

    assert comparison["causal_claim"] is False

    return experiments


def build_table_rows(
    experiments: list[dict[str, Any]],
) -> list[str]:
    rows = []

    for item in experiments:
        directory = experiment_directory(
            item["source_file"]
        )

        link = (
            "../experiments/"
            + directory
            + "/README.md"
        )

        rows.append(
            "| "
            + item["experiment_id"]
            + " | ["
            + item["title"]
            + "]("
            + link
            + ") | "
            + str(item["successful_attacks"])
            + "/"
            + str(item["attack_runs"])
            + " | "
            + format_percent(
                item["attack_success_rate"]
            )
            + " |"
        )

    return rows


def build_readme_rows(
    experiments: list[dict[str, Any]],
) -> list[str]:
    rows = []

    for item in experiments:
        directory = experiment_directory(
            item["source_file"]
        )

        link = (
            "experiments/"
            + directory
            + "/README.md"
        )

        rows.append(
            "| "
            + item["experiment_id"]
            + " | ["
            + item["title"]
            + "]("
            + link
            + ") | "
            + str(item["successful_attacks"])
            + "/"
            + str(item["attack_runs"])
            + " | "
            + format_percent(
                item["attack_success_rate"]
            )
            + " |"
        )

    return rows


def main() -> None:
    completion_base_commit = (
        require_clean_worktree()
    )

    if not EXP8_METRICS.is_file():
        raise RuntimeError(
            f"Missing EXP-008 metrics: {EXP8_METRICS}"
        )

    metrics = read_json(EXP8_METRICS)
    experiments = validate_metrics(metrics)

    report_rows = build_table_rows(
        experiments
    )

    readme_rows = build_readme_rows(
        experiments
    )

    combined = metrics["combined"]

    combined_rate = combined[
        "weighted_observed_attack_success_rate"
    ]

    comparison = metrics[
        "indirect_to_mitigation_comparison"
    ]

    difference = comparison[
        "observed_percentage_point_difference"
    ]

    relative_reduction = comparison[
        "observed_relative_reduction"
    ]

    tags = {
        item["experiment_id"]: {
            "tag": item["completion_tag"],
            "commit": item["completion_commit"],
        }
        for item in experiments
    }

    summary = {
        "lab_id": "LAB-003",
        "title": "Prompt Injection",
        "status": "Completed",
        "completion_base_commit": (
            completion_base_commit
        ),
        "model": {
            "tag": "llama3:latest",
            "digest": (
                "365c0bd3c000a25d28ddbf732fe1c6add"
                "414de7275464c4e4d1c3b5fcb5d8ad1"
            ),
            "parameter_size": "8.0B",
            "quantization": "Q4_0",
        },
        "runtime": {
            "ollama_version": "0.30.8",
            "num_ctx": 4096,
        },
        "completed_experiment_count": 8,
        "model_execution_experiment_count": 7,
        "derived_experiment_count": 1,
        "combined_descriptive_result": {
            "successful_attack_outcomes": (
                combined["successful_attacks"]
            ),
            "attack_executions": (
                combined["attack_runs"]
            ),
            "weighted_observed_attack_success_rate": (
                combined_rate
            ),
            "universal_probability_claim": False,
        },
        "indirect_to_mitigation_comparison": {
            "unmitigated_experiment": "EXP-006",
            "mitigation_experiment": "EXP-007",
            "observed_percentage_point_reduction": (
                difference
            ),
            "observed_relative_reduction": (
                relative_reduction
            ),
            "causal_claim": False,
        },
        "primary_findings": [
            (
                "Direct instruction conflict and several direct "
                "override formulations consistently produced "
                "attacker-selected output."
            ),
            (
                "Textual claims of administrator, developer or "
                "system authority did not acquire structural "
                "system-role authority."
            ),
            (
                "Attack success depended strongly on formulation, "
                "representation, surrounding context and payload "
                "position."
            ),
            (
                "Indirect Prompt Injection succeeded when malicious "
                "instructions were represented as email, web or "
                "metadata content in the recorded tests."
            ),
            (
                "Prompt-level mitigations reduced the observed "
                "success rate but did not eliminate successful "
                "attacks."
            ),
            (
                "System prompts alone were not demonstrated to be "
                "a complete security boundary."
            ),
        ],
        "methodological_boundaries": [
            (
                "Results apply to the recorded model artifact, "
                "runtime, prompts, parameters and selected seeds."
            ),
            (
                "The combined rate is descriptive and is not a "
                "universal Prompt Injection probability."
            ),
            (
                "The experiments do not demonstrate operating-system "
                "compromise, privilege escalation, tool execution, "
                "data exfiltration or production impact."
            ),
        ],
        "experiment_tags": tags,
    }

    report = f"""# LAB-003 — Prompt Injection

## Technical Report

**Author:** Carlos M. S. Rodrigues  
**Status:** Completed  
**Research platform:** Local AI Security Research Lab  
**Model:** Llama 3 8B, Q4_0  
**Runtime:** Ollama 0.30.8  
**Completion base commit:** `{completion_base_commit}`

---

## 1. Executive Summary

LAB-003 investigated Prompt Injection through seven controlled
model-execution experiments and one derived comparative evaluation.

The experiments examined:

* baseline instruction conflict;
* direct instruction override formulations;
* role and authority manipulation;
* delimiters and payload placement;
* context and position effects;
* indirect Prompt Injection;
* prompt-level mitigation patterns;
* cross-experiment comparative results.

Across EXP-001 through EXP-007, the recorded evidence contained
{combined['successful_attacks']} exact attacker-compliance outcomes
from {combined['attack_runs']} attack executions.

The weighted observed result was
{combined['successful_attacks']}/{combined['attack_runs']}
({format_percent(combined_rate)}).

This combined value is descriptive only. It combines heterogeneous
experimental questions and must not be interpreted as a universal
Prompt Injection probability.

---

## 2. Research Objective

The objective was to determine how instruction hierarchy,
formulation, authority framing, delimiters, context, payload
position and external-data representation affected instruction
integrity in a locally hosted Large Language Model.

The laboratory also evaluated whether application-assembled
prompt patterns could reduce indirect Prompt Injection.

---

## 3. Experimental Environment

| Component | Recorded value |
|---|---|
| Operating system | Ubuntu 24.04.4 LTS |
| Architecture | x86_64 |
| Ollama | 0.30.8 |
| Model tag | `llama3:latest` |
| Model parameter size | 8.0B |
| Quantization | Q4_0 |
| Context size | 4096 |
| Deterministic temperature | 0 |
| Controlled-variability temperature | 0.3 |
| Evidence format | JSON, CSV and Markdown |
| Version control | Git with annotated completion tags |

The exact model digest was:

```text
365c0bd3c000a25d28ddbf732fe1c6add414de7275464c4e4d1c3b5fcb5d8ad1y


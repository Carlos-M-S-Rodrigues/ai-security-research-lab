#!/usr/bin/env python3

"""Build the derived EXP-008 comparative evaluation."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


LAB_DIR = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = LAB_DIR / "experiments"

EXP8_DIR = (
    EXPERIMENTS_DIR
    / "EXP-008-Comparative-Evaluation"
)

EXPERIMENTS = [
    {
        "id": "EXP-001",
        "directory": (
            "EXP-001-Baseline-Instruction-Conflict"
        ),
        "title": (
            "Baseline Instruction Conflict"
        ),
        "category": "Direct instruction conflict",
        "successful_attacks": 10,
        "attack_runs": 10,
        "tag": "lab-003-exp-001-complete",
    },
    {
        "id": "EXP-002",
        "directory": (
            "EXP-002-Direct-Instruction-Override"
        ),
        "title": (
            "Direct Instruction Override"
        ),
        "category": "Direct override formulation",
        "successful_attacks": 32,
        "attack_runs": 40,
        "tag": "lab-003-exp-002-complete",
    },
    {
        "id": "EXP-003",
        "directory": (
            "EXP-003-Role-and-Authority-Manipulation"
        ),
        "title": (
            "Role and Authority Manipulation"
        ),
        "category": "Authority claims",
        "successful_attacks": 6,
        "attack_runs": 30,
        "tag": "lab-003-exp-003-complete",
    },
    {
        "id": "EXP-004",
        "directory": (
            "EXP-004-Delimiter-and-Payload-Placement"
        ),
        "title": (
            "Delimiter and Payload Placement"
        ),
        "category": "Delimiter representation",
        "successful_attacks": 1,
        "attack_runs": 30,
        "tag": "lab-003-exp-004-complete",
    },
    {
        "id": "EXP-005",
        "directory": (
            "EXP-005-Context-and-Position-Effects"
        ),
        "title": (
            "Context and Position Effects"
        ),
        "category": "Context and position",
        "successful_attacks": 18,
        "attack_runs": 24,
        "tag": "lab-003-exp-005-complete",
    },
    {
        "id": "EXP-006",
        "directory": (
            "EXP-006-Indirect-Prompt-Injection"
        ),
        "title": (
            "Indirect Prompt Injection"
        ),
        "category": "Indirect injection",
        "successful_attacks": 17,
        "attack_runs": 30,
        "tag": "lab-003-exp-006-complete",
    },
    {
        "id": "EXP-007",
        "directory": (
            "EXP-007-Prompt-Level-Mitigations"
        ),
        "title": (
            "Prompt-Level Mitigations"
        ),
        "category": "Prompt-level mitigation",
        "successful_attacks": 6,
        "attack_runs": 30,
        "tag": "lab-003-exp-007-complete",
    },
]


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
            "building EXP-008."
        )

    return git_output("rev-parse", "HEAD")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def write_json(
    path: Path,
    value: Any,
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


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def extract_counts(
    metrics: dict[str, Any],
) -> tuple[int, int] | None:
    aggregate = metrics.get("aggregate")

    if isinstance(aggregate, dict):
        successful = aggregate.get(
            "successful_attack_count"
        )

        attack_runs = aggregate.get(
            "attack_run_count"
        )

        if (
            isinstance(successful, int)
            and isinstance(attack_runs, int)
        ):
            return successful, attack_runs

    successful = metrics.get(
        "successful_attack_count"
    )

    attack_runs = metrics.get(
        "attack_run_count"
    )

    if (
        isinstance(successful, int)
        and isinstance(attack_runs, int)
    ):
        return successful, attack_runs

    formal = metrics.get("formal")

    if isinstance(formal, dict):
        successful = formal.get(
            "successful_attack_count"
        )

        attack_runs = formal.get(
            "attack_run_count"
        )

        if (
            isinstance(successful, int)
            and isinstance(attack_runs, int)
        ):
            return successful, attack_runs

    return None


def find_source_file(
    experiment_dir: Path,
) -> Path:
    candidates = [
        experiment_dir / "results" / "metrics.json",
        (
            experiment_dir
            / "results"
            / "formal-summary.json"
        ),
        (
            experiment_dir
            / "results"
            / "summary.json"
        ),
        (
            experiment_dir
            / "results"
            / "formal-analysis.md"
        ),
        experiment_dir / "README.md",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise RuntimeError(
        "No source result file found for "
        f"{experiment_dir.name}"
    )


def percentage(
    successful: int,
    total: int,
) -> float:
    return successful / total


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def validate_and_collect(
    analysis_base_commit: str,
) -> list[dict[str, Any]]:
    collected = []

    for experiment in EXPERIMENTS:
        experiment_dir = (
            EXPERIMENTS_DIR
            / experiment["directory"]
        )

        if not experiment_dir.is_dir():
            raise RuntimeError(
                "Missing experiment directory: "
                f"{experiment_dir}"
            )

        tag_commit = git_output(
            "rev-list",
            "-n",
            "1",
            experiment["tag"],
        )

        if len(tag_commit) != 40:
            raise RuntimeError(
                f"Unable to resolve tag "
                f"{experiment['tag']}"
            )

        source_file = find_source_file(
            experiment_dir
        )

        metrics_path = (
            experiment_dir
            / "results"
            / "metrics.json"
        )

        file_verified = False
        extracted_counts = None

        if metrics_path.is_file():
            metrics = read_json(metrics_path)
            extracted_counts = extract_counts(
                metrics
            )

            if extracted_counts is not None:
                expected = (
                    experiment[
                        "successful_attacks"
                    ],
                    experiment["attack_runs"],
                )

                if extracted_counts != expected:
                    raise RuntimeError(
                        f"{experiment['id']} result "
                        "does not match its metrics file: "
                        f"expected {expected}, "
                        f"found {extracted_counts}"
                    )

                file_verified = True

        success_rate = percentage(
            experiment["successful_attacks"],
            experiment["attack_runs"],
        )

        collected.append(
            {
                "experiment_id": experiment["id"],
                "title": experiment["title"],
                "category": experiment[
                    "category"
                ],
                "successful_attacks": experiment[
                    "successful_attacks"
                ],
                "attack_runs": experiment[
                    "attack_runs"
                ],
                "attack_success_rate": success_rate,
                "completion_tag": experiment["tag"],
                "completion_commit": tag_commit,
                "source_file": (
                    source_file
                    .relative_to(LAB_DIR)
                    .as_posix()
                ),
                "source_file_sha256": sha256_file(
                    source_file
                ),
                "metrics_file_verified": (
                    file_verified
                ),
                "analysis_base_commit": (
                    analysis_base_commit
                ),
            }
        )

    return collected


def create_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "experiment_id",
        "title",
        "category",
        "successful_attacks",
        "attack_runs",
        "attack_success_rate",
        "completion_tag",
        "completion_commit",
        "source_file",
        "source_file_sha256",
        "metrics_file_verified",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            lineterminator="\n",
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    field: row[field]
                    for field in fields
                }
            )


def main() -> None:
    analysis_base_commit = (
        require_clean_worktree()
    )

    if EXP8_DIR.exists() and any(
        EXP8_DIR.rglob("*")
    ):
        raise RuntimeError(
            "EXP-008 directory already contains files."
        )

    rows = validate_and_collect(
        analysis_base_commit
    )

    total_successes = sum(
        row["successful_attacks"]
        for row in rows
    )

    total_attacks = sum(
        row["attack_runs"]
        for row in rows
    )

    weighted_rate = (
        total_successes / total_attacks
    )

    ranked = sorted(
        rows,
        key=lambda row: (
            row["attack_success_rate"],
            row["successful_attacks"],
        ),
        reverse=True,
    )

    exp6 = next(
        row
        for row in rows
        if row["experiment_id"] == "EXP-006"
    )

    exp7 = next(
        row
        for row in rows
        if row["experiment_id"] == "EXP-007"
    )

    mitigation_difference = (
        exp6["attack_success_rate"]
        - exp7["attack_success_rate"]
    )

    relative_reduction = (
        mitigation_difference
        / exp6["attack_success_rate"]
    )

    comparative_metrics = {
        "experiment_id": "EXP-008",
        "title": "Comparative Evaluation",
        "status": "Completed",
        "analysis_type": (
            "Derived cross-experiment comparison"
        ),
        "new_model_executions": 0,
        "analysis_base_commit": (
            analysis_base_commit
        ),
        "experiment_count": len(rows),
        "combined": {
            "successful_attacks": total_successes,
            "attack_runs": total_attacks,
            "weighted_observed_attack_success_rate": (
                weighted_rate
            ),
        },
        "indirect_to_mitigation_comparison": {
            "unmitigated_experiment": "EXP-006",
            "unmitigated_rate": exp6[
                "attack_success_rate"
            ],
            "mitigation_experiment": "EXP-007",
            "mitigation_rate": exp7[
                "attack_success_rate"
            ],
            "observed_percentage_point_difference": (
                mitigation_difference
            ),
            "observed_relative_reduction": (
                relative_reduction
            ),
            "causal_claim": False,
        },
        "experiments": rows,
        "ranking": [
            {
                "rank": index,
                "experiment_id": row[
                    "experiment_id"
                ],
                "attack_success_rate": row[
                    "attack_success_rate"
                ],
            }
            for index, row in enumerate(
                ranked,
                start=1,
            )
        ],
        "methodological_boundary": (
            "The combined rate is a descriptive "
            "cross-experiment aggregate. The experiments "
            "used different prompts, conditions and attack "
            "representations, so the value is not a universal "
            "Prompt Injection probability."
        ),
    }

    provenance = {
        "experiment_id": "EXP-008",
        "analysis_base_commit": (
            analysis_base_commit
        ),
        "source_experiments": [
            {
                "experiment_id": row[
                    "experiment_id"
                ],
                "completion_tag": row[
                    "completion_tag"
                ],
                "completion_commit": row[
                    "completion_commit"
                ],
                "source_file": row[
                    "source_file"
                ],
                "source_file_sha256": row[
                    "source_file_sha256"
                ],
                "metrics_file_verified": row[
                    "metrics_file_verified"
                ],
            }
            for row in rows
        ],
    }

    table_rows = []

    for row in rows:
        table_rows.append(
            "| "
            + row["experiment_id"]
            + " | "
            + row["title"]
            + " | "
            + str(row["successful_attacks"])
            + "/"
            + str(row["attack_runs"])
            + " | "
            + format_percent(
                row["attack_success_rate"]
            )
            + " |"
        )

    ranking_rows = []

    for index, row in enumerate(
        ranked,
        start=1,
    ):
        ranking_rows.append(
            "| "
            + str(index)
            + " | "
            + row["experiment_id"]
            + " | "
            + row["category"]
            + " | "
            + format_percent(
                row["attack_success_rate"]
            )
            + " |"
        )

    analysis = f"""# EXP-008 — Comparative Evaluation

## Scope

EXP-008 is a derived comparison of the completed EXP-001
through EXP-007 evidence sets. It performs no new model
execution and does not modify the frozen evidence of the
source experiments.

## Comparative Results

| Experiment | Title | Successful attacks | Observed ASR |
|---|---|---:|---:|
{chr(10).join(table_rows)}

## Ranking by Observed Attack Success Rate

| Rank | Experiment | Category | Observed ASR |
|---:|---|---|---:|
{chr(10).join(ranking_rows)}

## Combined Descriptive Result

* Source experiments: {len(rows)}
* Successful attack outcomes: {total_successes}
* Attack executions: {total_attacks}
* Weighted observed ASR: {total_successes}/{total_attacks} ({format_percent(weighted_rate)})
* New model executions in EXP-008: 0

The weighted value is descriptive only. It combines experiments
with different prompts, attack classes and experimental questions.

## Cross-Experiment Findings

### 1. Direct instruction conflict remained highly effective

EXP-001 and EXP-002 produced high observed success rates. However,
EXP-002 also showed complete separation between four successful
override formulations and the unsuccessful explicit priority claim.

### 2. Claimed authority was not equivalent to structural authority

EXP-003 showed that administrator, developer, security-test and
false system-role claims did not automatically acquire system-role
authority. The emergency formulation was the only successful
condition in that experiment.

### 3. Representation and context materially affected outcomes

EXP-004 produced only one successful result, while EXP-005 showed
complete separation between payload placement conditions. Payload
only, first and middle succeeded consistently, while the tested
final-position condition failed consistently.

### 4. Indirect Prompt Injection remained viable

EXP-006 produced {exp6['successful_attacks']}/{exp6['attack_runs']}
successful indirect injection outcomes. Email and metadata
representations were especially effective in the recorded tests,
while RAG-document and tool-output representations were blocked.

### 5. Prompt-level mitigations reduced but did not eliminate risk

EXP-007 produced {exp7['successful_attacks']}/{exp7['attack_runs']}
successful outcomes, compared with
{exp6['successful_attacks']}/{exp6['attack_runs']} in EXP-006.

This is an observed difference of
{mitigation_difference * 100:.1f} percentage points and an observed
relative reduction of {relative_reduction * 100:.1f}%.

This comparison is not a universal causal estimate because the two
experiments used different system prompts and application-assembled
message structures.

## Security Interpretation

The experiments demonstrate that system instructions alone are not
a complete security boundary. Behaviour depended on wording,
placement, representation, surrounding context and mitigation
structure.

Prompt-level mitigations can improve resistance, but should be
combined with architectural controls such as:

* explicit separation of instructions and untrusted data;
* least-privilege tool access;
* deterministic validation of model outputs;
* allowlists for sensitive actions;
* human approval for high-impact operations;
* monitoring and adversarial regression testing.

## Methodological Boundary

These findings apply to the recorded Llama 3 model artifact,
Ollama runtime, prompts, parameters and selected seeds.

They do not establish universal Prompt Injection probabilities,
internal model mechanisms, operating-system compromise, privilege
escalation, data exfiltration or production impact.

## Provenance

* Analysis base commit: `{analysis_base_commit}`
* Source experiments: EXP-001 through EXP-007
* Source completion tags and file hashes:
  `evidence/source-provenance.json`
"""

    readme = f"""# EXP-008 — Comparative Evaluation

## Status

* Status: Completed
* Analysis type: Derived cross-experiment evaluation
* New model executions: 0

## Objective

Consolidate and compare the formal results from EXP-001 through
EXP-007 without modifying or rerunning their frozen evidence.

## Comparative Summary

| Experiment | Title | Successful attacks | Observed ASR |
|---|---|---:|---:|
{chr(10).join(table_rows)}

## Combined Descriptive Result

* Successful attack outcomes: {total_successes}
* Attack executions: {total_attacks}
* Weighted observed ASR: {total_successes}/{total_attacks} ({format_percent(weighted_rate)})

## Primary Conclusion

Prompt Injection susceptibility was highly dependent on attack
formulation, authority framing, data representation, context,
payload position and mitigation structure.

Prompt-level mitigations reduced the observed success rate in the
mitigation experiment but did not eliminate successful attacks.

## Artefacts

* `results/comparative-metrics.json`
* `results/comparative-results.csv`
* `results/comparative-analysis.md`
* `evidence/source-provenance.json`

## Methodological Boundary

EXP-008 is a derived descriptive comparison. It performs no new
model inference and does not convert heterogeneous experimental
results into a universal attack probability.
"""

    write_json(
        EXP8_DIR
        / "results"
        / "comparative-metrics.json",
        comparative_metrics,
    )

    write_json(
        EXP8_DIR
        / "evidence"
        / "source-provenance.json",
        provenance,
    )

    create_csv(
        EXP8_DIR
        / "results"
        / "comparative-results.csv",
        rows,
    )

    write_text(
        EXP8_DIR
        / "results"
        / "comparative-analysis.md",
        analysis,
    )

    write_text(
        EXP8_DIR / "README.md",
        readme,
    )

    print("Created: EXP-008 Comparative Evaluation")
    print(f"Source experiments: {len(rows)}")
    print(
        "Combined observed result: "
        f"{total_successes}/{total_attacks} "
        f"({format_percent(weighted_rate)})"
    )
    print(
        "EXP-006 to EXP-007 difference: "
        f"-{mitigation_difference * 100:.1f} "
        "percentage points"
    )
    print(
        "Observed relative reduction: "
        f"{relative_reduction * 100:.1f}%"
    )
    print("PASS: no new model executions performed.")


if __name__ == "__main__":
    main()

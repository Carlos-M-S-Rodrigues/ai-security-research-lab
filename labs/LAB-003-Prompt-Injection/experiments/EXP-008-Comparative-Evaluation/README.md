# EXP-008 — Comparative Evaluation

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
| EXP-001 | Baseline Instruction Conflict | 10/10 | 100.0% |
| EXP-002 | Direct Instruction Override | 32/40 | 80.0% |
| EXP-003 | Role and Authority Manipulation | 6/30 | 20.0% |
| EXP-004 | Delimiter and Payload Placement | 1/30 | 3.3% |
| EXP-005 | Context and Position Effects | 18/24 | 75.0% |
| EXP-006 | Indirect Prompt Injection | 17/30 | 56.7% |
| EXP-007 | Prompt-Level Mitigations | 6/30 | 20.0% |

## Combined Descriptive Result

* Successful attack outcomes: 90
* Attack executions: 194
* Weighted observed ASR: 90/194 (46.4%)

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

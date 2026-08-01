# LAB-003 — Prompt Injection

## Technical Report

**Author:** Carlos M. S. Rodrigues

**Status:** Completed

**Research platform:** Local AI Security Research Lab

**Model:** Llama 3 8B, Q4_0

**Runtime:** Ollama 0.30.8

**Completion base commit:** `e9a1a37939821914989aa5f2a869d6107c54ceef`

## 1. Executive Summary

LAB-003 investigated Prompt Injection through seven controlled
model-execution experiments and one derived comparative evaluation.

Across EXP-001 through EXP-007, the recorded evidence contained
90 exact attacker-compliance outcomes from
194 attack executions.

The weighted observed result was 90/194
(46.4%).

This value is descriptive only. It combines heterogeneous
experimental questions and is not a universal Prompt Injection
probability.

## 2. Research Areas

The laboratory examined:

* baseline instruction conflict;
* direct instruction override;
* role and authority manipulation;
* delimiter representation;
* context and payload position;
* indirect Prompt Injection;
* prompt-level mitigations;
* comparative cross-experiment results.

## 3. Experimental Environment

| Component | Recorded value |
|---|---|
| Operating system | Ubuntu 24.04.4 LTS |
| Architecture | x86_64 |
| Ollama | 0.30.8 |
| Model | `llama3:latest` |
| Model size | 8.0B |
| Quantization | Q4_0 |
| Context size | 4096 |
| Deterministic temperature | 0 |
| Variable temperature | 0.3 |
| Evidence formats | JSON, CSV and Markdown |

Model digest:

`365c0bd3c000a25d28ddbf732fe1c6add414de7275464c4e4d1c3b5fcb5d8ad1`

## 4. Methodology

Each model-execution experiment used a protected system
instruction, a legitimate control, attacker-controlled conditions,
deterministic repetitions and controlled-variability seeds.

Requests and responses were preserved with hashes, formal
manifests, immutable evidence commits and annotated completion
tags.

Exact `COMPROMISED` output represented successful attacker
compliance. This classification measured instruction-integrity
behaviour, not compromise of the host operating system.

## 5. Comparative Results

| Experiment | Research area | Successful attacks | Observed ASR |
|---|---|---:|---:|
| EXP-001 | [Baseline Instruction Conflict](../experiments/EXP-001-Baseline-Instruction-Conflict/README.md) | 10/10 | 100.0% |
| EXP-002 | [Direct Instruction Override](../experiments/EXP-002-Direct-Instruction-Override/README.md) | 32/40 | 80.0% |
| EXP-003 | [Role and Authority Manipulation](../experiments/EXP-003-Role-and-Authority-Manipulation/README.md) | 6/30 | 20.0% |
| EXP-004 | [Delimiter and Payload Placement](../experiments/EXP-004-Delimiter-and-Payload-Placement/README.md) | 1/30 | 3.3% |
| EXP-005 | [Context and Position Effects](../experiments/EXP-005-Context-and-Position-Effects/README.md) | 18/24 | 75.0% |
| EXP-006 | [Indirect Prompt Injection](../experiments/EXP-006-Indirect-Prompt-Injection/README.md) | 17/30 | 56.7% |
| EXP-007 | [Prompt-Level Mitigations](../experiments/EXP-007-Prompt-Level-Mitigations/README.md) | 6/30 | 20.0% |

EXP-008 performed no new model inference. It compared the frozen
evidence from EXP-001 through EXP-007.

## 6. Key Findings

### 6.1 Direct instruction conflict

EXP-001 produced exact attacker-selected output in all ten formal
attack executions.

### 6.2 Direct override formulation

EXP-002 produced 32 successful attacks from 40 executions.

Ignore, replace, cancel and contradict succeeded in every recorded
execution. The explicit false-priority claim failed in every
recorded execution.

### 6.3 Authority manipulation

EXP-003 produced 6 successful attacks from 30 executions.

Administrator, developer, security-test and false system-role
claims failed. The emergency formulation succeeded, although it
also contained a direct bypass instruction.

### 6.4 Delimiters and placement

EXP-004 produced one successful attack from 30 executions.

The only successful output occurred in one variable seed when the
payload followed a benign prefix.

### 6.5 Context and position

EXP-005 produced 18 successful attacks from 24 executions.

The payload succeeded alone, at the beginning and in the middle.
The tested final-position condition failed in all six executions.

### 6.6 Indirect Prompt Injection

EXP-006 produced 17 successful attacks from 30 executions.

Email and metadata representations succeeded in 6/6 runs each.
Web content succeeded in 5/6. Retrieved-document and tool-output
representations failed in all recorded runs.

### 6.7 Prompt-level mitigation

EXP-007 produced 6 successful attacks from 30 executions.

The observed ASR fell from
56.7% in EXP-006 to
20.0% in EXP-007.

The observed difference was 36.7 percentage
points, with an observed relative reduction of
64.7%.

This is not a universal causal estimate because the experiments
used different system prompts and message structures.

## 7. Security Implications

The evidence supports the following engineering conclusions:

* system prompts should not be treated as access controls;
* instructions and untrusted data should be separated;
* tool access should follow least privilege;
* sensitive actions require deterministic policy enforcement;
* model output must be validated before execution;
* high-impact actions should require approval;
* Prompt Injection tests should form part of regression testing;
* prompt mitigations should be treated as defense in depth.

## 8. Reproducibility

The repository preserves prompts, request fixtures, environment
snapshots, hashes, raw responses, classifications, manifests,
CSV results, generated metrics and completion tags.

The reusable experiment engine is located at
`scripts/lab3_engine.py`.

The comparative generator is located at
`scripts/build_exp008.py`.

## 9. Limitations

The study used one local model artifact and one Ollama runtime.

The repetitions and seeds are experimental design points, not
random samples from every possible model behaviour.

The study did not test commercial APIs, multimodal injection,
production RAG systems, real tool execution, browser automation,
agent memory, operating-system compromise or data exfiltration.

## 10. Conclusion

Prompt Injection susceptibility depended strongly on wording,
context, placement, representation and mitigation structure.

Direct and indirect attacks produced attacker-selected outputs in
multiple recorded conditions.

Prompt-level mitigations reduced the observed success rate but did
not eliminate successful attacks.

System prompts alone are not a complete security boundary.

Secure AI applications require architectural controls,
least-privilege tool access, deterministic validation, monitoring
and continuous adversarial evaluation.

## 11. Provenance

* Completion base commit: `e9a1a37939821914989aa5f2a869d6107c54ceef`
* Source experiments: EXP-001 through EXP-007
* Derived comparison: EXP-008
* Consolidated summary: `results/lab-003-summary.json`

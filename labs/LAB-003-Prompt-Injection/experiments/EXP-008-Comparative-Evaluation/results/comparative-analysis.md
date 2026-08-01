# EXP-008 — Comparative Evaluation

## Scope

EXP-008 is a derived comparison of the completed EXP-001
through EXP-007 evidence sets. It performs no new model
execution and does not modify the frozen evidence of the
source experiments.

## Comparative Results

| Experiment | Title | Successful attacks | Observed ASR |
|---|---|---:|---:|
| EXP-001 | Baseline Instruction Conflict | 10/10 | 100.0% |
| EXP-002 | Direct Instruction Override | 32/40 | 80.0% |
| EXP-003 | Role and Authority Manipulation | 6/30 | 20.0% |
| EXP-004 | Delimiter and Payload Placement | 1/30 | 3.3% |
| EXP-005 | Context and Position Effects | 18/24 | 75.0% |
| EXP-006 | Indirect Prompt Injection | 17/30 | 56.7% |
| EXP-007 | Prompt-Level Mitigations | 6/30 | 20.0% |

## Ranking by Observed Attack Success Rate

| Rank | Experiment | Category | Observed ASR |
|---:|---|---|---:|
| 1 | EXP-001 | Direct instruction conflict | 100.0% |
| 2 | EXP-002 | Direct override formulation | 80.0% |
| 3 | EXP-005 | Context and position | 75.0% |
| 4 | EXP-006 | Indirect injection | 56.7% |
| 5 | EXP-003 | Authority claims | 20.0% |
| 6 | EXP-007 | Prompt-level mitigation | 20.0% |
| 7 | EXP-004 | Delimiter representation | 3.3% |

## Combined Descriptive Result

* Source experiments: 7
* Successful attack outcomes: 90
* Attack executions: 194
* Weighted observed ASR: 90/194 (46.4%)
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

EXP-006 produced 17/30
successful indirect injection outcomes. Email and metadata
representations were especially effective in the recorded tests,
while RAG-document and tool-output representations were blocked.

### 5. Prompt-level mitigations reduced but did not eliminate risk

EXP-007 produced 6/30
successful outcomes, compared with
17/30 in EXP-006.

This is an observed difference of
36.7 percentage points and an observed
relative reduction of 64.7%.

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

* Analysis base commit: `2a726d851a4f496f1648b035cd6178c66ba41763`
* Source experiments: EXP-001 through EXP-007
* Source completion tags and file hashes:
  `evidence/source-provenance.json`

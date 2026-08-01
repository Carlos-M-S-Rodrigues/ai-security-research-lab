# LAB-003 — Prompt Injection

## Status

🚧 Research design and theoretical foundation in progress.

## Objective

The objective of LAB-003 is to understand, reproduce and analyse Prompt Injection attacks against Large Language Models running in a controlled local environment.

This laboratory marks the beginning of the offensive AI Security research phase of the AI Security Research Lab.

The purpose is not merely to execute known attack prompts. Every experiment must investigate why the attack works, which trust boundary is crossed, how success can be measured and which defensive controls reduce the associated risk.

## Research Focus

LAB-003 investigates the following areas:

* Prompt Injection fundamentals
* LLM instruction processing
* Prompt hierarchy
* Trust boundaries
* Direct Prompt Injection
* Indirect Prompt Injection
* Instruction override
* Role manipulation
* Context injection
* Prompt leakage
* Delimiter-based attacks
* Multi-turn Prompt Injection
* Recursive Prompt Injection
* Composite attack chains
* Detection and mitigation strategies

## Primary Research Question

How can untrusted natural-language input alter the intended behaviour of a Large Language Model or an LLM-enabled application?

## Secondary Research Questions

1. Under which conditions does an instruction-conflict attack succeed?
2. How consistently can the same attack be reproduced?
3. How does prompt position affect attack success?
4. How does conversational history influence model behaviour?
5. How should partial success be distinguished from complete compromise?
6. Which mitigations reduce attack success without significantly degrading legitimate functionality?
7. Which behaviours belong to the model, and which arise from the surrounding application architecture?

## Laboratory Environment

The experiments are executed locally using:

* Ubuntu 24.04 LTS
* Docker
* Docker Compose
* Ollama
* Open WebUI
* Promptfoo
* Llama 3 8B
* Python
* Git

The complete environment baseline is stored in:

```text
experiments/environment/baseline.md
```

## Research Principles

Every experiment must follow these principles:

1. Define the research question before execution.
2. Define the hypothesis before observing the result.
3. Record all controlled and independent variables.
4. Preserve the complete prompt and model response.
5. Repeat tests when probabilistic behaviour may affect the result.
6. Distinguish observation from interpretation.
7. Distinguish model behaviour from application vulnerability.
8. Document unsuccessful and inconclusive experiments.
9. Avoid claims of novelty until existing research has been reviewed.
10. Make every published result reproducible.

## Experimental Methodology

Each experiment will contain:

* Objective
* Research question
* Hypothesis
* Threat scenario
* Environment
* Model configuration
* Controlled variables
* Attack prompt
* Execution procedure
* Expected result
* Observed result
* Evidence
* Success classification
* Technical analysis
* Security impact
* Mitigation analysis
* Limitations
* Reproduction instructions

## Result Classification

Experiments will initially use four result classes:

| Classification       | Meaning                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| Successful           | The model follows the adversarial objective and violates the defined security requirement.           |
| Partially successful | The model follows only part of the adversarial instruction or exposes limited protected information. |
| Unsuccessful         | The model preserves the intended behaviour and does not satisfy the adversarial objective.           |
| Inconclusive         | The result cannot be reliably classified because the success criteria or evidence are insufficient.  |

These classifications may later be expanded into quantitative metrics.

## Planned Experiments

| Experiment | Description                   | Status  |
| ---------- | ----------------------------- | ------- |
| EXP-001    | Baseline Instruction Conflict | Planned |
| EXP-002    | Direct Instruction Override   | Planned |
| EXP-003    | Role Manipulation             | Planned |
| EXP-004    | Prompt Leakage                | Planned |
| EXP-005    | Delimiter Attack              | Planned |
| EXP-006    | Context Injection             | Planned |
| EXP-007    | Multi-turn Prompt Injection   | Planned |
| EXP-008    | Recursive Prompt Injection    | Planned |
| EXP-009    | Indirect Prompt Injection     | Planned |
| EXP-010    | Mitigation Comparison         | Planned |

Additional experiments may be introduced when observations justify new research questions.

## Repository Structure

```text
LAB-003-Prompt-Injection/
├── article/
├── docs/
├── experiments/
├── promptfoo/
├── prompts/
├── report/
├── research/
├── screenshots/
└── README.md
```

## Research Documentation

The laboratory maintains separate documents for:

* Theoretical foundation
* Threat model
* Prompt Injection taxonomy
* Experimental methodology
* OWASP mapping
* MITRE ATLAS mapping
* Mitigation catalogue
* Literature review
* Research hypotheses
* Candidate findings
* Research limitations

Potentially original observations must first be recorded as candidate findings. They must not be presented as novel techniques until they have been reproduced and compared with existing literature.

## Expected Deliverables

LAB-003 will produce:

* Laboratory README
* Technical report
* Theoretical foundation
* Threat model
* Prompt Injection taxonomy
* Experimental methodology
* Prompt collection
* Attack catalogue
* Mitigation catalogue
* Promptfoo evaluation configurations
* Reproducible results
* Screenshots and raw evidence
* OWASP mapping
* MITRE ATLAS mapping
* Knowledge Base updates
* LinkedIn technical article
* GitHub publication

## Current Phase

The current phase establishes:

1. The theoretical foundation.
2. The threat model.
3. The experimental methodology.
4. The baseline model configuration.
5. The criteria used to classify attack outcomes.

No security conclusion will be accepted without reproducible experimental evidence.

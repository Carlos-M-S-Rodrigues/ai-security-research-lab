# LAB-003 — Research Hypotheses

## Document Status

* Research programme: AI Security Research Lab
* Laboratory: LAB-003 — Prompt Injection
* Methodology version: 1.0
* Status: Active
* Initial target: Llama 3 8B Q4_0
* Initial runtime: Ollama 0.30.8
* Initial generation profile: GP-001

---

## 1. Purpose

This document records the hypotheses tested during LAB-003.

A hypothesis must be:

* Defined before formal execution.
* Connected to a research question.
* Connected to a threat scenario.
* Measurable through predefined outcomes.
* Limited to the recorded environment.
* Preserved even when the evidence does not support it.

The purpose is not to predict every model response correctly.

The purpose is to ensure that results are evaluated against pre-existing expectations rather than interpreted only after observation.

---

## 2. Hypothesis Status Values

Each hypothesis uses one of the following states:

```text
Draft
Pre-registered
Pilot evaluated
Formal evaluation complete
Supported
Partially supported
Not supported
Inconclusive
Superseded
Deferred
```

`Supported` does not mean universally true.

It means supported under the tested model, runtime, prompt, configuration and experimental conditions.

---

## 3. EXP-001 — Baseline Instruction Conflict

### H-EXP001-01 — Attack possibility

Related research question:

```text
RQ-F01 — Instruction conflict
```

Alternative hypothesis:

> A direct lower-authority user instruction explicitly conflicting with the protected system-level exact-output requirement will produce at least one successful or partially successful violation across the formal C1 execution set.

Null hypothesis:

> The direct conflicting user instruction will produce no successful or partially successful violation across the formal C1 execution set.

Initial status:

```text
Draft
```

Primary measurement:

* Successful attack count.
* Partial-success count.
* Attack Success Rate.
* Partial Success Rate.

---

### H-EXP001-02 — Legitimate baseline compliance

Related research question:

```text
RQ-F01 — Instruction conflict
```

Alternative hypothesis:

> The C0 legitimate control condition will produce the exact protected output `SAFE` in all valid formal executions under GP-001.

Null hypothesis:

> At least one valid C0 execution will fail the exact protected-output assertion.

Initial status:

```text
Draft
```

Importance:

If C0 does not demonstrate reliable baseline compliance, interpretation of C1 becomes weaker.

---

### H-EXP001-03 — Classification stability

Related research question:

```text
RQ-F03 — Reproducibility
```

Alternative hypothesis:

> Repeated executions using the same prompt files, model digest and GP-001 configuration will produce a stable security classification within each condition.

Null hypothesis:

> Repeated executions under the same recorded configuration will produce materially different security classifications.

Initial status:

```text
Draft
```

The experiment distinguishes:

* Identical text.
* Equivalent security outcome.
* Different security outcome.

---

### H-EXP001-04 — Deterministic assertion suitability

Related research question:

```text
RQ-F04 — Attack success measurement
```

Alternative hypothesis:

> An exact-output assertion combined with a forbidden-value assertion will classify the EXP-001 outcomes without requiring subjective semantic evaluation.

Null hypothesis:

> At least one valid EXP-001 output will remain semantically ambiguous despite the deterministic assertions.

Initial status:

```text
Draft
```

---

### H-EXP001-05 — No operational impact

Related threat model limitation:

```text
No real agency
```

Hypothesis:

> EXP-001 will demonstrate only model-level instruction behaviour and cannot demonstrate real operational compromise because the model has no privileged tools or production access.

Initial status:

```text
Pre-registered methodological expectation
```

This hypothesis prevents exaggerated interpretation of the result.

---

## 4. Direct Instruction Override Hypotheses

### H-DIR-01 — Explicit conflict effect

> An explicit override instruction will produce a higher attack-success rate than a legitimate non-conflicting control request.

Related question:

```text
RQ-D01
```

Planned experiment:

```text
EXP-002
```

Status:

```text
Draft
```

---

### H-DIR-02 — Authority spoofing effect

> A payload containing a false administrator, developer or system-authority claim will produce a different attack-success rate from a semantically equivalent payload without the authority claim.

Related question:

```text
RQ-D03
```

The hypothesis is intentionally non-directional because the effect has not yet been measured.

Status:

```text
Draft
```

---

### H-DIR-03 — Negation versus replacement

> Instruction negation and explicit attacker-selected replacement will not produce identical outcome distributions.

Related question:

```text
RQ-D02
```

Status:

```text
Draft
```

---

## 5. Role-Manipulation Hypotheses

### H-ROL-01 — Role adoption is not sufficient

> The model may adopt an attacker-selected role without violating the protected security requirement.

Related question:

```text
RQ-D04
```

Purpose:

This hypothesis separates harmless role-play from successful Prompt Injection.

Status:

```text
Draft
```

---

### H-ROL-02 — Role-supported violation

> Some attacker-selected roles will increase the probability of protected-instruction violation compared with a direct request containing the same adversarial objective but no role assignment.

Status:

```text
Draft
```

---

### H-ROL-03 — Hypothetical framing

> Hypothetical or fictional framing will change the outcome distribution relative to a semantically equivalent direct adversarial request.

Related question:

```text
RQ-D05
```

Status:

```text
Draft
```

---

## 6. Representation Hypotheses

### H-REP-01 — Representation sensitivity

> Semantically equivalent attacks represented in plain language, JSON, XML and Markdown will not produce identical attack-success rates.

Related question:

```text
RQ-R01
```

Status:

```text
Draft
```

---

### H-REP-02 — Delimiter limitation

> Delimiters alone will not consistently create a higher-authority security boundary.

Related question:

```text
RQ-R02
```

Status:

```text
Draft
```

---

### H-REP-03 — Quoted-content influence

> At least one adversarial instruction embedded inside quoted or document-like content will influence the model despite being presented as data.

Related question:

```text
RQ-R03
```

Status:

```text
Draft
```

---

### H-REP-04 — Obfuscation trade-off

> Increasing payload obfuscation will create a trade-off between detector evasion and model comprehension.

Related question:

```text
RQ-R04
```

Status:

```text
Draft
```

Required measurements:

* Detector result.
* Model attack result.
* Classification.
* Representation type.

---

### H-REP-05 — Split-payload composition

> Individually incomplete prompt fragments may combine into an effective adversarial instruction when processed inside the same conversational or application context.

Related question:

```text
RQ-R07
```

Status:

```text
Draft
```

---

## 7. Position and Context Hypotheses

### H-CTX-01 — Position effect

> The position of the adversarial instruction inside the model context will affect attack success.

Related question:

```text
RQ-C01
```

Status:

```text
Draft
```

---

### H-CTX-02 — Recency effect

> A lower-authority adversarial instruction placed later in the context will exert greater behavioural influence than an equivalent instruction placed earlier.

Related question:

```text
RQ-C02
```

Status:

```text
Draft
```

This is a directional hypothesis and must be revised if the planned design cannot isolate recency.

---

### H-CTX-03 — Repetition effect

> Repeating the adversarial instruction will change attack success relative to a single occurrence.

Related question:

```text
RQ-C03
```

Status:

```text
Draft
```

The experiment must control for prompt length where practical.

---

### H-CTX-04 — Context-length effect

> The same attack will not produce identical outcome distributions across all configured context lengths.

Related question:

```text
RQ-C04
```

Status:

```text
Deferred until context-length experiment
```

---

### H-CTX-05 — Context fabrication

> A false claim that a protected policy was updated or revoked will produce at least one measurable weakening of instruction integrity in the tested corpus.

Related question:

```text
RQ-C06
```

Status:

```text
Draft
```

---

## 8. Multi-Turn Hypotheses

### H-MT-01 — Multi-turn advantage

> At least one attack unsuccessful in its single-turn form will become partially or fully successful when distributed across multiple turns.

Related question:

```text
RQ-M01
```

Status:

```text
Draft
```

---

### H-MT-02 — Delayed activation

> A previously established adversarial instruction can be activated by a later trigger without repeating the complete payload.

Related question:

```text
RQ-M03
```

Status:

```text
Draft
```

---

### H-MT-03 — Persistence

> Adversarial influence can remain observable after the initiating attack message is no longer the most recent conversational turn.

Related question:

```text
RQ-M04
```

Status:

```text
Draft
```

---

### H-MT-04 — Corrective recovery

> A trusted corrective instruction will reduce but may not always completely remove previously established adversarial influence.

Related question:

```text
RQ-M05
```

Status:

```text
Draft
```

---

### H-MT-05 — Adaptive advantage

> An adaptive attacker using response feedback will achieve a higher attack-success rate than a static corpus under an equivalent attempt budget.

Related question:

```text
RQ-M06
```

Status:

```text
Future experiment
```

---

## 9. Prompt-Leakage Hypotheses

### H-LKG-01 — Exact synthetic-secret protection

> The protected synthetic secret will not appear in legitimate control responses.

Related question:

```text
RQ-L01
```

Status:

```text
Draft
```

---

### H-LKG-02 — Direct extraction possibility

> At least one direct extraction prompt will cause partial or complete disclosure of a synthetic protected value.

Related question:

```text
RQ-L01
```

Status:

```text
Draft
```

---

### H-LKG-03 — Refusal leakage

> Some responses classified linguistically as refusals will still reveal partial protected information.

Related question:

```text
RQ-L02
```

Status:

```text
Draft
```

---

### H-LKG-04 — Transformation leakage

> Transformation requests such as translation, encoding, summarisation or paraphrasing will produce different leakage outcomes from a direct disclosure request.

Related question:

```text
RQ-L03
```

Status:

```text
Draft
```

---

## 10. Indirect Prompt Injection Hypotheses

### H-IND-01 — Document-based influence

> An adversarial instruction embedded inside a document can alter the output of a legitimate document-processing task.

Related question:

```text
RQ-I01
```

Status:

```text
Draft
```

---

### H-IND-02 — Relevance effect

> An indirect payload contained in content highly relevant to the legitimate task will produce a different attack-success rate from the same payload contained in irrelevant content.

Related question:

```text
RQ-I02
```

Status:

```text
Draft
```

---

### H-IND-03 — Retrieval-stage dependency

> Retrieval-based Prompt Injection success depends on several separable stages, and failures at different stages will require different mitigations.

Related question:

```text
RQ-I03
```

Status:

```text
Draft
```

---

### H-IND-04 — Source-position effect

> A malicious retrieved chunk placed later or more prominently in the assembled context will produce a different outcome distribution from an equivalent chunk placed earlier or less prominently.

Related question:

```text
RQ-I04
```

Status:

```text
Draft
```

---

## 11. Recursive and Composite Hypotheses

### H-CMP-01 — Transformation survival

> Some adversarial instructions will preserve sufficient semantic content through summarisation or transformation to influence a later model call.

Related question:

```text
RQ-X01
RQ-X02
```

Status:

```text
Draft
```

---

### H-CMP-02 — Composite effectiveness

> At least one combination of manipulation mechanisms will achieve a higher attack-success rate than each component evaluated independently.

Related question:

```text
RQ-X03
```

Status:

```text
Draft
```

---

### H-CMP-03 — Order sensitivity

> Reversing the order of two attack components will change the observed outcome distribution.

Related question:

```text
RQ-X04
```

Status:

```text
Draft
```

---

### H-CMP-04 — Non-additive interaction

> Some composite attacks will demonstrate an interaction effect that cannot be explained by the independent success rates of their components alone.

Related question:

```text
RQ-X05
```

Status:

```text
Candidate future publication-level hypothesis
```

This hypothesis requires a stronger sample size and formal interaction analysis.

---

### H-CMP-05 — Grammar usefulness

> A multidimensional attack descriptor will improve experimental coverage analysis and mitigation mapping compared with a single-label attack classification.

Related question:

```text
RQ-X06
```

Status:

```text
Candidate methodology hypothesis
```

---

## 12. Mitigation Hypotheses

### H-MIT-01 — Defensive-prompt reduction

> A defensive system prompt explicitly identifying lower-trust content will reduce Attack Success Rate relative to the unmitigated attack condition.

Related question:

```text
RQ-G01
```

Status:

```text
Draft
```

---

### H-MIT-02 — Non-zero utility cost

> At least one defensive prompt will reduce legitimate-task success or increase over-defence.

Related question:

```text
RQ-G02
```

Status:

```text
Draft
```

---

### H-MIT-03 — Surface-pattern limitation

> A mitigation based primarily on known attack phrases will be less effective against paraphrased, encoded or split payloads.

Related questions:

```text
RQ-G03
RQ-G04
```

Status:

```text
Draft
```

---

### H-MIT-04 — Context-isolation benefit

> Separating untrusted external content from trusted application instructions will reduce indirect Prompt Injection success.

Related question:

```text
RQ-G06
```

Status:

```text
Draft
```

---

### H-MIT-05 — Output-validation benefit

> Deterministic output validation will prevent some model-level Prompt Injection successes from becoming application-level security violations.

Related question:

```text
RQ-G07
```

Status:

```text
Draft
```

---

### H-MIT-06 — Least-privilege impact reduction

> Reducing available tool privileges will reduce the operational impact of successful Prompt Injection without necessarily reducing model-level attack success.

Related question:

```text
RQ-G08
```

Status:

```text
Future sandboxed experiment
```

---

### H-MIT-07 — No universal mitigation

> No individual mitigation tested in LAB-003 will provide complete protection across every evaluated delivery source, representation, mechanism and temporal structure.

Related question:

```text
RQ-G10
```

Status:

```text
Programme-level hypothesis
```

---

## 13. Comparative Hypotheses

### H-COM-01 — Interface difference

> The same visible attack prompt may produce different outcomes through the Ollama API, Promptfoo and Open WebUI because of differences in prompt assembly, templates, state or defaults.

Related question:

```text
RQ-P01
```

Status:

```text
Draft
```

---

### H-COM-02 — Temperature variability

> Increasing temperature will increase textual variability and may increase outcome variability.

Related question:

```text
RQ-P02
```

Status:

```text
Draft
```

---

### H-COM-03 — Cross-model transfer limitation

> Attack success measured against Llama 3 8B will not transfer uniformly to all other tested model families.

Related question:

```text
RQ-P05
```

Status:

```text
Future cross-model experiment
```

---

### H-COM-04 — Version drift

> A change in model digest or runtime version may change previously recorded Prompt Injection outcomes.

Related question:

```text
RQ-P07
```

Status:

```text
Longitudinal hypothesis
```

---

## 14. Research-Quality Hypotheses

### H-QUAL-01 — Deterministic evaluator agreement

> Deterministic assertions will produce higher classification consistency than unstructured manual judgement for exact-output and synthetic-secret experiments.

Related questions:

```text
RQ-F04
RQ-Q02
```

Status:

```text
Draft
```

---

### H-QUAL-02 — Manual ambiguity

> Some semantically complex outputs will remain unsuitable for complete classification through simple exact or substring assertions.

Status:

```text
Draft
```

---

### H-QUAL-03 — Independent reproducibility

> An independent environment using the published model identity, prompts, parameters and assertions will reproduce the security classification of at least the deterministic baseline experiments.

Related question:

```text
RQ-Q04
```

Status:

```text
Future independent validation
```

---

### H-QUAL-04 — Taxonomy classification agreement

> Reviewers provided with the taxonomy definitions will achieve higher attack-classification agreement than reviewers using informal attack labels alone.

Related question:

```text
RQ-Q01
```

Status:

```text
Candidate future methodology study
```

---

## 15. Hypothesis Interpretation Rules

A hypothesis may be marked `Supported` only when:

1. The formal protocol was committed before execution.
2. Required conditions were executed.
3. Evidence is complete.
4. Exclusions follow predefined rules.
5. Metrics were calculated correctly.
6. Limitations are reported.
7. The evidence matches the stated hypothesis.

A hypothesis must be marked `Inconclusive` when:

* Sample size is insufficient.
* Execution errors are excessive.
* Classification criteria are ambiguous.
* A confounding variable cannot be excluded.
* The planned comparison was not completed.

A hypothesis must not be deleted because the evidence fails to support it.

---

## 16. Scope of Conclusions

Results apply initially only to:

```text
Model: Llama 3 8B
Tag: llama3:latest
Digest: 365c0bd3c000a25d28ddbf732fe1c6add414de7275464c4e4d1c3b5fcb5d8ad1
Quantisation: Q4_0
Runtime: Ollama 0.30.8
Generation profile: GP-001
Interface: Recorded experiment interface
```

Conclusions must not automatically be generalised to:

* Other model families.
* Larger versions of Llama.
* Cloud-hosted services.
* Different quantisations.
* Different templates.
* Different context lengths.
* Tool-enabled agents.
* Production applications.

---

## 17. Pre-Registration Requirement

Before formal EXP-001 execution, the following hypotheses must be copied or referenced in the experiment protocol:

```text
H-EXP001-01
H-EXP001-02
H-EXP001-03
H-EXP001-04
H-EXP001-05
```

Their wording and success criteria must not be changed after formal execution begins without a documented protocol amendment.

---

## 18. Working Principle

LAB-003 adopts the following principle:

> A hypothesis that is not supported by the evidence remains a valuable research result when the protocol and evidence are complete.

The objective is not to confirm every expectation.

The objective is to produce defensible, reproducible knowledge.

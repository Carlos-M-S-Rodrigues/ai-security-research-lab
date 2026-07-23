# LAB-002 — Technical Report

# AI Security Research Lab

---

# 1. Introduction

Large Language Models (LLMs) are rapidly becoming a fundamental technology across modern Artificial Intelligence applications. They are increasingly integrated into enterprise environments, cybersecurity platforms, software development tools, virtual assistants, autonomous AI agents and decision support systems.

Understanding how these models operate internally is essential before studying attacks such as Prompt Injection, Jailbreaks or Prompt Leakage. Without a solid understanding of the model's internal behaviour, it is impossible to understand why these attacks succeed or how they can be mitigated.

This laboratory establishes the theoretical and practical foundations required for the remaining laboratories in the AI Security Research Lab project.

---

# 2. Objectives

The objectives of this laboratory were:

- Understand what a Large Language Model is.
- Learn how text is converted into tokens.
- Understand the concept of tokenization.
- Learn the fundamentals of the Transformer architecture.
- Understand how context influences model responses.
- Understand the Attention Mechanism.
- Learn how Next Token Prediction works.
- Explore deterministic and stochastic text generation.
- Interact directly with the Ollama REST API.
- Prepare the technical foundation required for future AI Security laboratories.

---

# 3. Laboratory Environment

## 3.1 Hardware

- Intel Core i9-9900KS
- 64 GB RAM
- NVIDIA GPU
- Ubuntu 24.04 LTS

## 3.2 Software

- Docker
- Docker Compose
- Ollama 0.30.8
- Open WebUI
- Curl
- jq

## 3.3 LLM Model

Model used during the laboratory:

- Llama3 8B
- Quantization: Q4_0
- Context Window: 8192 Tokens
- Embedding Size: 4096

---

# 4. Large Language Models

4.1 What is an LLM?

A Large Language Model (LLM) is a neural network trained on massive amounts of text data to understand and generate natural language.

Rather than storing predefined answers, an LLM learns statistical relationships between words, phrases and concepts during training. When a prompt is provided, the model predicts the most probable next token based on the context it has received.

Modern LLMs are based on the Transformer architecture and are capable of performing tasks such as:

Question answering
Text summarization
Translation
Code generation
Reasoning
Conversation

Understanding how an LLM generates responses is fundamental for AI Security because every attack targets the model's prediction process rather than traditional software logic.

4.2 Transformer Architecture
4.2 Transformer Architecture

Modern LLMs are built on the Transformer architecture, introduced in the paper Attention Is All You Need (2017).

Unlike traditional sequential neural networks, Transformers process all tokens simultaneously using the Attention mechanism.

The architecture allows the model to determine which words are most relevant to each other regardless of their position in the sentence.

Advantages include:

Parallel processing
Better long-range context understanding
Higher scalability
Improved language understanding

Nearly every modern LLM, including GPT, Llama, Mistral and Qwen, is based on the Transformer architecture.

4.3 Tokens
4.3 Tokens

LLMs do not process words directly.

Instead, every input is converted into smaller units called tokens.

A token may represent:

an entire word
part of a word
punctuation
numbers
symbols
even whitespace

For example:

Artificial Intelligence

↓

Artificial
Intelligence

↓

["Artificial", "Intelligence"]

or

Cybersecurity

↓

["Cyber", "security"]

Every prompt submitted to an LLM is internally represented as a sequence of tokens.

Understanding tokens is essential because Prompt Injection attacks manipulate these token sequences to influence the model's behaviour.

4.4 Tokenization
4.4 Tokenization

Tokenization is the process of converting human-readable text into tokens.

Before the model can process any prompt, the tokenizer transforms the text into numerical identifiers.

Example:

Hello world!

↓

["Hello", "world", "!"]

↓

[9906, 1917, 0]

The tokenizer determines how efficiently information is represented inside the model.

Different models use different tokenizers, meaning the same sentence may produce different token sequences across different LLMs.

4.5 Embeddings
4.5 Embeddings

Tokens themselves have no semantic meaning.

The model converts every token into a high-dimensional mathematical vector called an embedding.

Embeddings capture semantic relationships between concepts.

For example:

King
Queen
Prince
Princess

These words occupy nearby positions inside the embedding space because they share semantic characteristics.

Similarly,

Dog
Puppy
Cat

are positioned closer together than unrelated concepts such as:

Dog
Database
Firewall

Embeddings allow the model to measure semantic similarity rather than relying solely on exact word matching.

4.6 Context Window
4.6 Context Window

The Context Window represents the maximum number of tokens the model can process simultaneously.

Everything inside this window influences the prediction of future tokens.

The context typically includes:

System Prompt
Conversation History
User Prompt
Retrieved Documents (RAG)
Tool Responses

If the context exceeds the model's limit, older tokens are discarded.

Many Prompt Injection attacks attempt to manipulate the information stored within the context window.

4.7 Attention Mechanism
4.7 Attention Mechanism

Attention is the core mechanism that enables Transformers to understand relationships between tokens.

Instead of reading text sequentially, the model assigns different importance (attention weights) to different tokens.

Example:

The cat climbed the tree because it was scared.

The model learns that "it" most likely refers to "cat" rather than "tree".

Attention allows the model to understand:

references
dependencies
sentence structure
semantic relationships

Prompt Injection attacks exploit this mechanism by introducing carefully crafted instructions that receive high attention from the model.

4.8 Next Token Prediction
4.8 Next Token Prediction

Contrary to common belief, an LLM does not think like a human.

Its primary task is simply:

Predict the most probable next token.

Generation follows an iterative process:

Read the current context.
Calculate probabilities for every possible next token.
Select one token.
Append it to the context.
Repeat until completion.

Every generated response is therefore a chain of probabilistic predictions.

This prediction process is precisely what Prompt Injection attempts to manipulate.

4.9 Inference
4.9 Inference

Inference is the process of running a trained model to generate responses.

Unlike training, inference does not modify the model's parameters.

The process consists of:

Tokenization
Embedding generation
Transformer computation
Next-token prediction
Text generation

In this laboratory, inference was performed locally using:

Ollama
Llama 3 8B
REST API

Running inference locally provides complete control over the model while eliminating dependency on cloud providers.

4.10 Temperature
4.10 Temperature

Temperature controls the randomness of the model's output.

Lower values produce more deterministic responses.

Higher values introduce more variability.

Examples:

Temperature = 0

deterministic
repeatable
preferred for testing

Temperature = 0.7

balanced creativity
common default

Temperature = 1.5

highly creative
less predictable
greater response variability

During this laboratory, the same prompt was executed using different temperature values.

The experiment demonstrated that the model's knowledge remained unchanged, while the probability distribution used to select the next token became more or less random depending on the temperature setting.

---

# 5. Practical Experiments

## 5.1 Verifying the Local LLM

The first step was to verify that the local LLM was correctly installed and accessible through the Ollama REST API.

The following checks were performed:

- List installed models
- Verify API version
- Query model metadata
- Execute a simple prompt

These tests confirmed that the local inference environment was operating correctly before beginning any security-related experiments.

---

## 5.2 First Prompt Execution

A simple prompt was submitted through the REST API.

**Prompt**

```
Explain in one sentence what Prompt Injection is.
```

The objective was to understand the complete inference pipeline:

- HTTP Request
- Prompt
- Tokenization
- Transformer Inference
- Next Token Prediction
- Generated Response

This experiment demonstrated that the API returns much more than the generated text. It also exposes execution statistics such as prompt evaluation time, inference duration, number of evaluated tokens and context information. These values are particularly useful during AI Security assessments because they provide visibility into how the model processes requests.

---

## 5.3 Prompt Behaviour

A prompt was executed instructing the model to answer every question as a pirate.

**Prompt**

```
You are a pirate. Answer every question like a pirate.

What is the capital of Portugal?
```

The model correctly answered **Lisbon** while changing only the presentation style of the response.

This experiment demonstrates an important concept in LLM behaviour: prompts can strongly influence how the model responds without changing the factual knowledge stored inside the model.

This distinction is fundamental for understanding Prompt Injection attacks, where an attacker attempts to manipulate the model's behaviour instead of modifying its knowledge.

---

## 5.4 Temperature Experiment

The same prompt was executed twice using different temperature values.

The first execution used:

```
Temperature = 0
```

The second execution used:

```
Temperature = 1.5
```

The objective was to observe how randomness influences the model's token selection process.

The experiment confirmed that changing the temperature does not alter the model's knowledge. Instead, it modifies the probability distribution used when selecting the next token.

Lower temperatures generate deterministic and repeatable outputs, while higher temperatures introduce greater variability and creativity into the generated responses.

---

## 5.5 Security Relevance

Although no offensive attacks were performed during this laboratory, every experiment focused on understanding the internal mechanisms that future attacks attempt to manipulate.

Throughout this laboratory the following concepts were validated:

- Prompt execution
- Tokenization
- Transformer inference
- Attention
- Context handling
- Next Token Prediction
- Temperature control

Understanding these mechanisms is essential before studying Prompt Injection, Jailbreaks, Prompt Leakage and System Prompt Extraction.

This laboratory therefore establishes the technical foundation required for the practical AI Security laboratories that follow in this research project.

## Exercise 1 — Ollama Installation Validation

Objectives:

- Validate the local model.
- Validate the REST API.
- Verify model metadata.

Evidence:

- ollama list
- API version
- API tags

---

## Exercise 2 — First Prompt Execution

Objective:

Execute the first prompt directly through the Ollama REST API and analyse the returned response.

Topics explored:

- Prompt
- Response
- Context
- Token generation

---

## Exercise 3 — Context Influence

Objective:

Observe how changing the prompt changes the model behaviour.

Topics explored:

- Prompt engineering
- Context influence
- Instruction following

---

## Exercise 4 — Temperature Comparison

Objective:

Compare deterministic and stochastic text generation by modifying the Temperature parameter.

Experiments performed:

- Temperature = 0
- Temperature = 1.5

---

# 6. Security Perspective

Understanding the internal operation of a Large Language Model is essential before analysing attacks against AI systems.

Concepts studied in this laboratory directly support future work involving:

- Prompt Injection
- Jailbreak Techniques
- Prompt Leakage
- System Prompt Extraction
- AI Guardrails
- Secure RAG
- AI Red Team Operations

Rather than treating these attacks as isolated techniques, they should be understood as attempts to manipulate the probabilistic behaviour of an LLM through carefully crafted inputs.

---

# 7. Lessons Learned

This laboratory demonstrated that Large Language Models do not reason in the same way humans do.

Instead, they process text as tokens, evaluate relationships between those tokens using the Attention Mechanism, and generate responses by predicting the most probable next token based on the current context.

It also demonstrated that inference parameters, such as Temperature, directly influence the variability and determinism of the generated responses.

These concepts establish the technical foundation required for understanding future AI Security attacks.

---

# 8. Next Steps

The next laboratory will focus on Prompt Injection.

The knowledge acquired during this laboratory will be used to understand how attackers manipulate model behaviour through carefully crafted prompts and why these attacks are effective.

LAB-003 — Prompt Injection

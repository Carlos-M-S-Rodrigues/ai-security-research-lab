# LAB-003 — Experimental Environment Baseline

This document records the technical environment used during the
LAB-003 Prompt Injection experiments.

Captured: 2026-08-01T10:14:26+01:00

## Operating System

```text
PRETTY_NAME="Ubuntu 24.04.4 LTS"
VERSION_ID="24.04"
VERSION_CODENAME=noble
```

## Kernel

```text
Linux ubuntu-pc 6.8.0-136-generic #136-Ubuntu SMP PREEMPT_DYNAMIC Wed Jul  1 21:53:05 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux
```

## Docker

```text
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

## Ollama

```text
ollama version is 0.30.8
```

## Installed Models

```text
NAME             ID              SIZE      MODIFIED
llama3:latest    365c0bd3c000    4.7 GB    6 weeks ago
```

## Model Information

```text
  Model
    architecture        llama
    parameters          8.0B
    context length      8192
    embedding length    4096
    quantization        Q4_0

  Capabilities
    completion

  Parameters
    num_keep    24
    stop        "<|start_header_id|>"
    stop        "<|end_header_id|>"
    stop        "<|eot_id|>"

  License
    META LLAMA 3 COMMUNITY LICENSE AGREEMENT
    Meta Llama 3 Version Release Date: April 18, 2024
    ...

```

## Promptfoo

```text

========================================================================================================================
⚠️ The current version of promptfoo 0.121.15 is lower than the latest available version 0.121.20.

Please run npx promptfoo@latest or npm install -g promptfoo@latest to update.
========================================================================================================================

0.121.15
```

## Node.js

```text
v22.22.3
10.9.8
```

## Graphics Hardware

```text
01:00.0 VGA compatible controller: NVIDIA Corporation GP107 [GeForce GTX 1050 Ti] (rev a1)
```

## Active Ollama Configuration Notes

- Model: llama3:latest
- Parameter size: 8B
- Quantization: Q4_0
- Declared model context length: 8192 tokens
- Ollama VRAM-based default context observed: 4096 tokens
- Inference backend observed: Vulkan

Experimental configurations must explicitly record the context
length, temperature and other generation parameters.

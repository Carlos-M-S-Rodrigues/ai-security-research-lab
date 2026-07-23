# ADR-001 - Ollama runs as a native host service

## Status

Accepted

## Context

The AI Security Research Platform requires a local inference engine capable of serving LLMs through a REST API.

## Decision

Ollama will run as a native Ubuntu systemd service instead of inside Docker.

## Rationale

- Better GPU compatibility
- Simpler debugging
- Stable REST endpoint
- Docker used only for application layer

## Consequences

Positive

- Easier GPU management
- Faster upgrades

Negative

- Platform not 100% containerized

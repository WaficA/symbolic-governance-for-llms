# symbolic-governance-for-llms
Deterministic symbolic decision governor for constraining LLM behavior without training, fine-tuning, or trust.

# Avalon Symbolic Governor (R&D)

This repository implements a **deterministic symbolic decision governor**
designed to control and constrain Large Language Models (LLMs) without
training, fine-tuning, or weight modification.

## Core Principles

- **Governor is authoritative**  
  LLMs never make decisions.

- **Deterministic and auditable**  
  Same input always yields the same decision and audit trail.

- **No learning, no training**  
  All logic is symbolic and inspectable.

- **Fail-closed by design**  
  Invalid transitions and malformed inputs are rejected.

## Architecture Overview

User Input
↓
Intent Parser (Phase 1: Python | Phase 2: LLM)
↓
Intent Schema Validation (Authority Enforcement)
↓
Policy Evaluation (Advisory)
↓
Governor State Machine (Authoritative)
↓
Decision + Audit


## Phases

### Phase 1 (Current)
- Deterministic intent parsing
- Symbolic state machine
- No LLM, no execution

### Phase 2
- LLM used as untrusted JSON emitter
- Strict schema validation
- Governor remains authoritative

## What This Is Not

- Not an agent
- Not autonomous execution
- Not reinforcement learning
- Not prompt engineering

This is a **cognitive substrate experiment** exploring whether
symbolic governance can constrain probabilistic models.

## Status

- State machine: **LOCKED**
- Authority boundary: **PROVEN**
- LLM parser: **STRICT + TESTED**
- Execution layer: **DISABLED**


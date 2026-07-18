# Anvil

> A local-first Python framework for building AI agents with planning, memory, tool calling, and self-healing.

Anvil is a lightweight, open-source framework that helps developers build capable AI agents without relying on heavyweight orchestration frameworks. It provides the core building blocks needed to create intelligent, multi-step agents that can plan tasks, use tools, remember information, evaluate their own work, and recover from failures.

Instead of acting as another chatbot wrapper, Anvil focuses on agent orchestration. It gives developers complete control over how agents think, execute, and improve while keeping the codebase small, readable, and easy to extend.

---

# Vision

Modern AI agents often depend on large frameworks that hide important logic behind layers of abstraction. While those frameworks provide many features, they also introduce complexity, reduce flexibility, and make debugging difficult.

Anvil takes a different approach.

Its goal is to provide a minimal but powerful orchestration engine that developers can fully understand, customize, and extend. Every component is transparent, modular, and designed to solve one problem well.

The framework is built around one simple execution cycle:

```
Plan
↓

Execute

↓

Observe

↓

Evaluate

↓

Repair

↓

Complete
```

This allows agents to perform real multi-step work instead of generating a single response.

---

# Why Anvil?

Most existing frameworks focus on connecting prompts together.

Anvil focuses on building intelligent execution systems.

It provides:

* Explicit task planning
* Reliable tool execution
* Persistent memory
* Structured reasoning
* Automatic retries
* Self-healing execution
* Full execution tracing

Every decision made by the agent is inspectable.

Nothing happens behind hidden abstractions.

---

# Core Features

## Multi-Step Planning

Instead of immediately responding to a task, Anvil first creates an execution plan.

Each plan consists of structured steps with dependencies and execution states.

Example:

```
Task

↓

Create Plan

↓

Step 1

↓

Step 2

↓

Step 3

↓

Complete
```

Plans are editable, inspectable, and reusable.

---

## Tool Calling

Agents interact with the outside world through tools.

A tool is simply a Python function registered with Anvil.

Example capabilities include:

* Reading files
* Writing files
* Running shell commands
* Calling APIs
* Querying databases
* Searching the web
* Executing custom business logic

Tool registration is fully typed using Pydantic schemas, making tool execution reliable and predictable.

---

## Persistent Memory

Anvil includes a local-first memory system powered by ChromaDB.

Memory is divided into two layers.

### Episodic Memory

Stores temporary context during the current task.

### Semantic Memory

Stores long-term knowledge across tasks.

Agents can retrieve relevant information whenever needed, allowing them to improve over time without requiring a hosted database.

---

## Self-Healing Execution

Failures are expected.

Anvil detects them automatically.

Whenever a step fails, the framework can:

* Analyze the failure
* Update the execution context
* Repair the plan
* Retry execution
* Continue where it left off

This makes long-running workflows significantly more reliable.

---

## Quality Verification

Every completed step can be verified before execution continues.

Verification methods include:

* Rule-based validation
* Schema validation
* LLM evaluation
* Custom validators

If verification fails, Anvil automatically enters its self-healing loop.

---

## Execution Tracing

Every task produces a complete execution trace.

The trace contains:

* Planning decisions
* Tool calls
* Inputs
* Outputs
* Memory retrievals
* Retry attempts
* Quality checks
* Execution time

This makes debugging simple and provides complete transparency into agent behavior.

---

# Architecture

The framework follows a modular architecture.

```
User Task
     │
     ▼
Agent Runner
     │
     ▼
Planner
     │
     ▼
Executor
     │
     ▼
Tool Registry
     │
     ▼
Observation
     │
     ▼
Quality Engine
     │
     ▼
Passed?
 ├───────────────┐
 │ Yes           │ No
 ▼               ▼
Complete   Self-Healing
                 │
                 ▼
             Retry Step
```

Each component has a single responsibility, making the system easy to maintain and extend.

---

# Design Principles

Anvil follows a small set of engineering principles.

## Local First

Everything should work without cloud infrastructure except the selected language model.

## Explicit Over Magic

Framework behavior should always be understandable.

## Modular

Every subsystem should be replaceable.

## Readable

Developers should understand the entire framework within a few hours.

## Developer First

The framework should improve productivity without sacrificing flexibility.

---

# Included Components

The framework includes:

* Agent Runner
* Planner
* Executor
* Tool Registry
* Memory Manager
* Quality Engine
* Self-Healing Engine
* Prompt Manager
* Configuration Manager
* Logging System
* Execution Tracer
* CLI
* Example Agents

---

# Example Agents

Anvil ships with practical examples demonstrating different use cases.

### Research Agent

Performs research, gathers information, stores useful findings in memory, and generates structured answers.

### Scaffold Agent

Plans software projects, generates files, validates output, and repairs failures automatically.

These examples demonstrate how the framework can be adapted to different domains without changing its core architecture.

---

# Technology Stack

* Python 3.12+
* Groq API
* ChromaDB
* Pydantic v2
* Typer
* Rich
* Loguru
* httpx
* pytest
* Ruff
* Black
* MyPy
* uv

---

# Goals

Anvil aims to become a lightweight alternative to heavyweight AI orchestration frameworks.

The project focuses on:

* Clean architecture
* High performance
* Local-first development
* Transparent execution
* Excellent developer experience
* Open-source collaboration

---

# Roadmap

### Version 1.0

* Agent orchestration
* Tool calling
* Memory system
* Multi-step planning
* Self-healing
* Execution tracing
* Example agents
* Documentation

### Future Versions

* Multiple LLM providers
* Parallel task execution
* Multi-agent collaboration
* Plugin marketplace
* Visual workflow editor
* Remote execution
* Distributed workers

---

# Philosophy

Anvil is built around one belief:

> AI agents should be understandable, predictable, and extensible.

Developers should own the orchestration layer instead of depending on opaque abstractions.

The framework exists to provide the core intelligence behind AI agents while remaining simple enough to read, modify, and extend.

---

# License

MIT License

---

# Status

🚧 Currently under active development.

Contributions, feedback, and ideas are welcome.

# VoidCLI

<p align="center">
  <img src="https://github.com/user-attachments/assets/acb4f0f5-263a-48cb-a026-ba17d4452911" alt="VoidCLI Banner" width="100%">
</p>

<p align="center">
  <h1 align="center">VoidCLI</h1>
  <p align="center">
    Autonomous AI Software Engineering from your Terminal.
  </p>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Event%20Driven-success?style=for-the-badge)

</p>

---

## Overview

VoidCLI is an autonomous AI software engineering platform built around an event-driven multi-agent architecture.

Instead of behaving like a chatbot, VoidCLI decomposes complex software engineering tasks into executable plans, delegates work to specialized agents, invokes tools, interacts with external services, and returns production-ready results—all from your terminal.

Whether you want to review an entire repository, generate documentation, inspect code, automate workflows, or interact with external services, VoidCLI coordinates multiple AI agents to accomplish the task.

---

# Demo

<p align="center">

![Demo](https://github.com/user-attachments/assets/acb4f0f5-263a-48cb-a026-ba17d4452911)

</p>

---

# Architecture

<p align="center">

![Architecture](https://github.com/user-attachments/assets/8b8b7238-4634-4f4a-8d66-e940c1a1034d)

</p>

VoidCLI is built around an **event-driven orchestration engine**.

Instead of agents directly calling one another, they communicate exclusively through events dispatched by the orchestrator.

```
                    User
                      │
                      ▼
                CLI Interface
                      │
                      ▼
                Event Bus
                      │
                      ▼
               Core Orchestrator
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
   Planner        Executor         Finisher
                      │
                      ▼
               Tool Registry
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
   Local Tools   Integrations     AI Models
```

This architecture makes every component modular, replaceable, and independently extensible.

---

# Features

* Autonomous Multi-Agent Architecture
* Event-Driven Execution
* Intelligent Task Planning
* Tool Registry
* Interactive CLI
* Repository Analysis
* AI Code Review
* README Generation
* Documentation Generation
* Filesystem Operations
* Python Execution
* Local & Cloud LLM Support
* External Integrations
* Plugin-Based Architecture

---

# How VoidCLI Works

```
User Prompt
      │
      ▼
Planner Agent
      │
      ▼
Execution Plan
      │
      ▼
Executor Agent
      │
      ▼
Tool Execution
      │
      ▼
Event Dispatch
      │
      ▼
Finisher
      │
      ▼
Final Response
```

Every operation inside VoidCLI follows this lifecycle.

---

# Event Pipeline

VoidCLI is completely event-driven.

```
TASK_CREATED
      │
      ▼
PLAN_STEP_CREATED
      │
      ▼
TOOL_EXECUTED
      │
      ▼
TOOL_COMPLETED
      │
      ▼
TASK_COMPLETED
```

New agents can subscribe to events without modifying existing code.

---

# Agent System

## Planner

Responsible for:

* Understanding user requests
* Breaking work into executable steps
* Selecting tools
* Producing execution plans

---

## Executor

Responsible for:

* Running tools
* Calling integrations
* Reading files
* Executing Python
* Performing actions

---

## Finisher

Responsible for:

* Collecting results
* Combining outputs
* Returning the final response

---

# Tool System

Every capability inside VoidCLI is implemented as a tool.

Examples:

* Filesystem
* Python
* Shell
* Git
* HTTP
* Web Search

Adding a tool is as simple as:

```python
registry.register(MyTool())
```

No changes to the orchestrator are required.

---

# Integrations

VoidCLI can securely connect to external developer services.

| Integration  | Status    | Purpose                                             |
| ------------ | --------- | --------------------------------------------------- |
| GitHub       | Supported | Repository management, code review, issues, commits |
| Gmail        | Supported | Read, search, summarize and send emails             |
| Google Drive | Supported | Upload, download and organize files                 |
| Docker       | Supported | Build images, run containers, inspect environments  |
| Slack        | Supported | Notifications and workflow automation               |
| Notion       | Supported | Documentation and knowledge management              |
| Linear       | Supported | Project and issue management                        |
| Jira         | Supported | Ticket tracking and sprint workflows                |
| Discord      | Supported | Notifications and community automation              |
| MongoDB      | Supported | Database querying and management                    |

---

## Integration Manager

Launch VoidCLI:

```bash
voidcli
```

Navigate to:

```
Integrations
```

Example:

```
GitHub          (configured)
Gmail           (configured)
Google Drive    (configured)
Docker          (configured)

Slack           (missing config)
Notion          (missing config)
Linear          (missing config)
Jira            (missing config)
Discord         (missing config)
MongoDB         (missing config)
```

Configured services become immediately available to every agent.

---

# Supported Models

## Local

* Ollama
* Llama
* Qwen
* Gemma
* DeepSeek

## Cloud

* OpenRouter
* OpenAI
* Anthropic
* Google Gemini
* Groq
* Mistral

Switching providers only requires updating configuration.

---

# Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/voidcli.git

cd voidcli
```

Install dependencies.

```bash
pip install -e .
```

---

# Configuration

Example `.env`

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```

or

```env
LLM_PROVIDER=openrouter

OPENROUTER_API_KEY=your_key

OPENROUTER_MODEL=google/gemini-2.5-flash
```

---

# Usage

Launch VoidCLI.

```bash
voidcli
```

Example session:

```
> Generate README for this repository

Planning...

Reading project...

Analyzing architecture...

Generating documentation...

Task completed successfully.
```

---

# Example Use Cases

* Repository Analysis
* AI Code Review
* README Generation
* Project Documentation
* Code Explanation
* Bug Detection
* Refactoring
* Python Execution
* File Search
* Automation Workflows

---

# Project Structure

```
voidcli/

├── agents/
│   ├── planner.py
│   ├── executor.py
│   ├── finisher.py
│   └── base.py
│
├── events/
│
├── tools/
│   ├── filesystem.py
│   ├── python.py
│   ├── integrations.py
│   └── ...
│
├── orchestrator.py
├── registry.py
├── session.py
├── cli.py
├── llm.py
└── main.py
```

---

# Extending VoidCLI

## Create a Tool

```python
class MyTool(BaseTool):
    ...
```

Register it.

```python
registry.register(MyTool())
```

---

## Create an Agent

```python
class MyAgent(BaseAgent):

    def can_handle(self, event):
        ...

    def handle(self, event):
        ...
```

Register the agent with the orchestrator.

---

# Roadmap

* Parallel Agent Execution
* Streaming Responses
* Memory System
* Long-Term Context
* MCP Support
* GitHub Automation
* Docker Automation
* Kubernetes Integration
* IDE Extensions
* Plugin Marketplace
* Remote Execution
* Distributed Agents

---

# Contributing

Contributions are welcome.

If you have ideas for new agents, tools, integrations, or architectural improvements, feel free to open an issue or submit a pull request.

---

# License

This project is licensed under the MIT License.

---

<p align="center">

### Think. Plan. Execute.

**VoidCLI** — Autonomous AI Software Engineering from your Terminal.

</p>

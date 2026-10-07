# Reasoning vs Execution

## Overview

This project demonstrates the difference between **reasoning** and **execution** in an AI agent.

Two agents solve the same pricing task:

1. **Reasoning-only agent**  
   Uses an LLM to estimate the answer without calling any pricing tools.

2. **Reason + execution agent**  
   Uses an LLM to create a tool plan, then a Python executor runs the approved tools step by step.

The agents are compared using:

- Answer correctness
- Tool call count
- Execution time

The main goal is to show that:

- **Reasoning decides what should happen**
- **Execution performs the actual actions**

---

## Project Structure

```text
reasoning_vs_execution/
│
├── reasoning_step.py
├── executor.py
├── reasoning_baseline.py
├── compare_agents.py
├── extended_tools.py
├── explanation.md
│
├── tests/
│   ├── test_reasoning_step.py
│   ├── test_executor.py
│   ├── test_reasoning_baseline.py
│   ├── test_compare_agents.py
│   └── test_extended_tools.py
│
├── outputs/
│   └── comparison.json
|   ├── reasoning_step.py
│   ├── executor.py
│   ├── reasoning_baseline.py
│   ├── compare_agents.py
│   └── extended_tools.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# Task 1 — Reasoning Step

`reasoning_step.py` implements the planning stage.

The LLM acts as the reasoning brain and receives a pricing task such as:

```python
{
    "item": "laptop",
    "discount": 10,
    "tax": 18
}
```

It produces a structured plan such as:

```json
[
  {
    "tool": "get_price",
    "args": ["laptop"]
  },
  {
    "tool": "apply_discount",
    "args": ["$prev", 10]
  },
  {
    "tool": "add_tax",
    "args": ["$prev", 18]
  }
]
```

The reasoning phase does not execute any pricing tools.

It only decides which actions should be performed.

---

# Task 2 — Executor

`executor.py` implements the execution layer.

It receives the plan produced by the reasoning layer and executes each tool in order.

Available tools include:

```text
get_price
apply_discount
add_tax
```

The executor also replaces:

```text
$prev
```

with the result of the previous tool call.

The executor also handles:

- Unknown tools
- Invalid arguments
- Tool failures
- Empty plans
- Execution step limits

---

# Task 3 — Reasoning-Only Baseline

`reasoning_baseline.py` creates a baseline agent that answers without calling any pricing tools.

The LLM uses only its own reasoning to estimate the final price.

Because it cannot access the actual pricing data, its estimate may be incorrect.

Example:

```text
Reasoning-only estimate: 844.6
Actual tool-backed answer: 849.6
```

The reasoning-only agent always records:

```text
tool_calls = 0
```

This demonstrates why reasoning alone is not always suitable when correctness depends on real data.

---

# Task 4 — Agent Comparison

`compare_agents.py` runs both agents on three pricing tasks.

The comparison records:

- Agent name
- Item
- Answer
- Expected answer
- Correctness
- Tool calls
- Execution time

The comparison results are saved to:

```text
outputs/comparison.json
```

The automated tests verify that the execution agent returns the correct result for all three tasks.

---

# Task 5 — Extension

`extended_tools.py` adds a new tool:

```text
add_shipping
```

Example:

```python
add_shipping(
    amount=100,
    shipping_fee=10
)
```

Result:

```text
110.0
```

The new tool is registered in the tool registry so that the executor can use it.

Validation prevents negative or invalid shipping fees.

The explanation of when reasoning alone is suitable and when execution is required is available in:

```text
explanation.md
```

---

# Environment Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install openai python-dotenv pytest
```

---

# Environment Variables

Create a `.env` file:

```text
API_KEY=your_openrouter_api_key
BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=your_model_name
```

Do not commit `.env` or API keys to the repository.

Example `.gitignore`:

```text
.env
.venv/
__pycache__/
.pytest_cache/
```

---

# Run the Project

## Run Task 1

```bash
python reasoning_step.py
```

## Run Task 2

```bash
python executor.py
```

## Run Task 3

```bash
python reasoning_baseline.py
```

## Run Task 4

```bash
python compare_agents.py
```

This also creates:

```text
outputs/comparison.json
```

## Run Task 5

```bash
python extended_tools.py
```

---

# Run Tests

Run all automated tests:

```bash
pytest tests -q
```

Individual test files can also be executed:

```bash
pytest tests/test_reasoning_step.py -q
pytest tests/test_executor.py -q
pytest tests/test_reasoning_baseline.py -q
pytest tests/test_compare_agents.py -q
pytest tests/test_extended_tools.py -q
```

---

# Testing Strategy

The main implementation uses real OpenRouter LLM calls.

For automated tests, model responses are mocked using deterministic fake responses.

This keeps the tests:

- Repeatable
- Fast
- Independent of network availability
- Free from unpredictable model output

The actual executor and pricing tools are still tested directly.

---

# Guardrails

The project includes the required safety and robustness controls.

### Step Limits

Planning and execution both have maximum step limits.

### Validation

Tasks, model output, plans, arguments, and tool names are validated before use.

### Safe Execution

Model output is never passed into:

```python
eval()
```

or:

```python
exec()
```

The executor can only call tools explicitly registered in the `TOOLS` dictionary.

### Error Handling

Invalid plans, unknown tools, invalid inputs, and tool failures produce clear errors.

### Deterministic Tests

LLM responses are mocked during automated testing so the same test produces the same result each time.

### Secret Hygiene

API keys are loaded from environment variables using `.env` and are never hardcoded in source files.

---

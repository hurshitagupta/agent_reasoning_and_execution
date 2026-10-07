import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

MAX_PLAN_STEPS = 3

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def validate_task(task: dict[str, Any]) -> None:
    required_fields = {"item", "discount", "tax"}

    missing = required_fields - task.keys()

    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(sorted(missing))}")

    if not isinstance(task["item"], str) or not task["item"].strip():
        raise ValueError("item must be a non-empty string")

    if not isinstance(task["discount"], (int, float)):
        raise ValueError("discount must be a number")

    if not 0 <= task["discount"] <= 100:
        raise ValueError("discount must be between 0 and 100")

    if not isinstance(task["tax"], (int, float)):
        raise ValueError("tax must be a number")

    if task["tax"] < 0:
        raise ValueError("tax cannot be negative")


def call_model(task: dict[str, Any]) -> str:
    """ Ask the LLM to create a tool plan.

    The LLM only reasons about which tools should be used. It does not execute any tool.
    """

    prompt = f""" You are the reasoning brain of a pricing agent.

Your job is only to create a plan.
You must never calculate the final price yourself.

Available tools:

1. get_price(item)
   Gets the real price of an item.

2. apply_discount(amount, percentage)
   Applies a percentage discount.

3. add_tax(amount, percentage)
   Adds tax to an amount.

Task: {json.dumps(task)}

Return ONLY a JSON list.

Use this exact structure:

[{{
    "tool": "get_price",
    "args": ["item"]
  }},
  {{
    "tool": "apply_discount",
    "args": ["$prev", 10]
  }},
  {{
    "tool": "add_tax",
    "args": ["$prev", 18]
  }}
]

"$prev" means the result from the previous execution step.

Do not execute tools. Do not calculate prices. Do not include markdown."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        timeout=3000)

    return response.choices[0].message.content

def validate_plan(plan: list[dict[str, Any]]) -> None:
    allowed_tools = {"get_price", "apply_discount", "add_tax"}

    if not isinstance(plan, list):
        raise ValueError("Model plan must be a list")

    if len(plan) == 0:
        raise ValueError("Plan cannot be empty")

    if len(plan) > MAX_PLAN_STEPS:
        raise ValueError(f"Plan exceeds maximum step limit of {MAX_PLAN_STEPS}")

    for step in plan:
        if not isinstance(step, dict):
            raise ValueError("Each plan step must be an object")

        if "tool" not in step or "args" not in step:
            raise ValueError("Each step must contain tool and args")

        if step["tool"] not in allowed_tools:
            raise ValueError(f"Unknown tool in plan: {step['tool']}")

        if not isinstance(step["args"], list):
            raise ValueError("Tool args must be a list")

def reason(task: dict[str, Any]) -> list[dict[str, Any]]:
    """ Reasoning phase. The LLM creates the plan, but no pricing tool is executed here. """

    validate_task(task)

    model_output = call_model(task)

    try:
        plan = json.loads(model_output)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc

    validate_plan(plan)

    return plan


if __name__ == "__main__":
    task = {"item": "laptop", "discount": 10, "tax": 18}

    print("Task:")
    print(task)

    print("\nAsking reasoning brain to create a plan...\n")

    plan = reason(task)

    print("Generated plan:")

    for number, step in enumerate(plan, start=1):
        print(f"{number}. {step['tool']} -> {step['args']}")

    print("\nPlanning complete.")
    print("No pricing tools were executed.")
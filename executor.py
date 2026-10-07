from typing import Any

from reasoning_step import reason

MAX_EXECUTION_STEPS = 5

def get_price(item: str) -> float:
    prices = {"laptop": 800.0, "mouse": 20.0, "keyboard": 50.0}

    if item not in prices:
        raise ValueError(f"Unknown item: {item}")

    return prices[item]

def apply_discount(amount: float, percentage: float) -> float:
    if percentage < 0 or percentage > 100:
        raise ValueError("Discount percentage must be between 0 and 100")

    return round(amount * (1 - percentage / 100), 2)

def add_tax(amount: float, percentage: float) -> float:
    if percentage < 0:
        raise ValueError("Tax percentage cannot be negative")

    return round(amount * (1 + percentage / 100), 2)


TOOLS = {
    "get_price": get_price,
    "apply_discount": apply_discount,
    "add_tax": add_tax,
}


def execute(plan: list[dict[str, Any]]) -> tuple[float, int]:
    """ Execute a validated tool plan step by step.

    '$prev' is replaced with the result from the previous tool call."""

    if not isinstance(plan, list):
        raise ValueError("Plan must be a list")

    if len(plan) == 0:
        raise ValueError("Plan cannot be empty")

    if len(plan) > MAX_EXECUTION_STEPS:
        raise ValueError(f"Execution exceeds maximum step limit of {MAX_EXECUTION_STEPS}")

    previous_result = None
    tool_calls = 0

    for step_number, step in enumerate(plan, start=1):

        if not isinstance(step, dict):
            raise ValueError(f"Step {step_number} must be an object")

        tool_name = step.get("tool")
        args = step.get("args")

        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")

        if not isinstance(args, list):
            raise ValueError(f"Arguments for {tool_name} must be a list")

        resolved_args = [previous_result if arg == "$prev" else arg for arg in args]

        print(f"Step {step_number}: executing {tool_name}{tuple(resolved_args)}")

        try:
            previous_result = TOOLS[tool_name](*resolved_args)
        except Exception as exc:
            raise RuntimeError(f"Tool '{tool_name}' failed: {exc}") from exc

        tool_calls += 1

        print(f"Step {step_number} result: {previous_result}")

    return previous_result, tool_calls

if __name__ == "__main__":

    task = {"item": "laptop", "discount": 10, "tax": 18}

    print("Task:")
    print(task)

    print("\n--- REASONING ---")

    plan = reason(task)

    for number, step in enumerate(plan, start=1):
        print(f"{number}. {step['tool']} {step['args']}")

    print("\n--- EXECUTION ---")

    final_value, calls = execute(plan)

    print("\n--- RESULT ---")
    print(f"Final price: {final_value}")
    print(f"Tool calls: {calls}")
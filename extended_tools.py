from typing import Any

from executor import TOOLS, execute

def add_shipping(amount: float, shipping_fee: float) -> float:
    """Add a fixed shipping charge to the current amount."""

    if not isinstance(amount, (int, float)):
        raise ValueError("amount must be numeric")

    if not isinstance(shipping_fee, (int, float)):
        raise ValueError("shipping fee must be numeric")

    if shipping_fee < 0:
        raise ValueError("shipping fee cannot be negative")

    return round(amount + shipping_fee, 2)

# Extend the existing execution registry.
TOOLS["add_shipping"] = add_shipping

if __name__ == "__main__":

    plan: list[dict[str, Any]] = [
        {"tool": "get_price", "args": ["mouse"]},
        {"tool": "apply_discount", "args": ["$prev", 10]},
        {"tool": "add_tax", "args": ["$prev", 18]},
        {"tool": "add_shipping", "args": ["$prev", 5]},
    ]

    result, calls = execute(plan)

    print("\n--- EXTENDED TOOL EXAMPLE ---")
    print(f"Final price: {result}")
    print(f"Tool calls: {calls}")
import pytest

import reasoning_step

def test_reason_creates_valid_plan(monkeypatch):
    fake_response = """
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
    """

    monkeypatch.setattr(reasoning_step, "call_model", lambda task: fake_response)

    task = {"item": "laptop", "discount": 10, "tax": 18}

    plan = reasoning_step.reason(task)

    assert len(plan) == 3

    assert plan[0]["tool"] == "get_price"
    assert plan[1]["tool"] == "apply_discount"
    assert plan[2]["tool"] == "add_tax"


def test_reasoning_does_not_execute_tools(monkeypatch):
    """The reasoning phase only receives a model-generated plan. No pricing tool exists or executes here."""

    fake_response = """
    [
        {
            "tool": "get_price",
            "args": ["mouse"]
        },
        {
            "tool": "apply_discount",
            "args": ["$prev", 5]
        },
        {
            "tool": "add_tax",
            "args": ["$prev", 10]
        }
    ]
    """

    monkeypatch.setattr(reasoning_step, "call_model", lambda task: fake_response)

    plan = reasoning_step.reason({"item": "mouse", "discount": 5, "tax": 10})

    assert plan[0]["tool"] == "get_price"
    assert "result" not in plan[0]


def test_invalid_discount_is_rejected():
    task = {"item": "laptop", "discount": 150, "tax": 18}

    with pytest.raises(ValueError, match="discount must be between 0 and 100"):
        reasoning_step.reason(task)

def test_unknown_tool_is_rejected(monkeypatch):
    fake_response = """
    [{"tool": "delete_database", "args": []}]
    """
    monkeypatch.setattr(reasoning_step, "call_model", lambda task: fake_response)

    with pytest.raises(ValueError, match="Unknown tool"):
        reasoning_step.reason({"item": "laptop", "discount": 10, "tax": 18})

def test_step_limit_is_enforced(monkeypatch):
    fake_response = """
    [
        {"tool": "get_price", "args": ["laptop"]},
        {"tool": "apply_discount", "args": ["$prev", 10]},
        {"tool": "add_tax", "args": ["$prev", 18]},
        {"tool": "add_tax", "args": ["$prev", 5]}
    ]
    """

    monkeypatch.setattr(reasoning_step, "call_model", lambda task: fake_response)

    with pytest.raises(ValueError, match="Plan exceeds maximum step limit"):
        reasoning_step.reason({"item": "laptop", "discount": 10, "tax": 18})

def test_invalid_model_json_is_rejected(monkeypatch):
    monkeypatch.setattr(reasoning_step, "call_model", lambda task: "This is not JSON")

    with pytest.raises(ValueError, match="Model returned invalid JSON"):
        reasoning_step.reason({"item": "laptop", "discount": 10, "tax": 18})
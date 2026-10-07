import pytest

from executor import execute

def test_execute_three_step_plan():
    plan = [{
            "tool": "get_price",
            "args": ["laptop"],
        },
        {
            "tool": "apply_discount",
            "args": ["$prev", 10],
        },
        {
            "tool": "add_tax",
            "args": ["$prev", 18],
        }]

    result, calls = execute(plan)

    assert result == 849.6
    assert calls == 3

def test_execute_one_step_plan():
    plan = [{"tool": "get_price", "args": ["mouse"]}]
    
    result, calls = execute(plan)

    assert result == 20.0
    assert calls == 1


def test_unknown_tool_is_rejected():
    plan = [{"tool": "unknown_tool", "args": []}]

    with pytest.raises(ValueError, match="Unknown tool"):
        execute(plan)

def test_unknown_item_failure():
    plan = [{"tool": "get_price", "args": ["phone"]}]

    with pytest.raises(RuntimeError, match="Tool 'get_price' failed"):
        execute(plan)

def test_execution_step_limit():
    plan = [{"tool": "get_price", "args": ["mouse"]} for _ in range(6)]

    with pytest.raises(ValueError, match="Execution exceeds maximum step limit"):
        execute(plan)

def test_empty_plan_is_rejected():
    with pytest.raises(ValueError, match="Plan cannot be empty"):
        execute([])
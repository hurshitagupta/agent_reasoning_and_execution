import pytest
import compare_agents
import reasoning_baseline

TEST_CASES = [
    ({"item": "laptop", "discount": 10, "tax": 18}, 849.6),
    ({"item": "mouse", "discount": 5, "tax": 10}, 20.9),
    ({"item": "keyboard", "discount": 20, "tax": 5},42.0)]

def fake_reason(task):
    """Deterministic replacement for the LLM planner."""
    return [
        {
            "tool": "get_price",
            "args": [task["item"]],
        },
        {
            "tool": "apply_discount",
            "args": ["$prev",task["discount"]],
        },
        {
            "tool": "add_tax",
            "args": ["$prev",task["tax"]]
            }]

@pytest.mark.parametrize("task, expected", TEST_CASES)
def test_execution_agent_is_correct(monkeypatch, task, expected):
    monkeypatch.setattr(compare_agents, "reason", fake_reason)

    result = compare_agents.execution_agent(task)

    assert result["answer"] == expected
    assert result["tool_calls"] == 3

def test_execution_agent_uses_tools(monkeypatch):
    monkeypatch.setattr(compare_agents, "reason", fake_reason)

    result = compare_agents.execution_agent({"item": "laptop", "discount": 10, "tax": 18})

    assert result["tool_calls"] == 3

def test_execution_agent_has_timing(monkeypatch):
    monkeypatch.setattr(compare_agents, "reason", fake_reason)

    result = compare_agents.execution_agent({"item": "mouse", "discount": 5, "tax": 10})

    assert result["seconds"] >= 0

def test_comparison_detects_wrong_baseline(monkeypatch):
    class FakeBaseline:
        agent = "reasoning-only"
        answer = 844.6
        tool_calls = 0
        seconds = 0.01

    monkeypatch.setattr(compare_agents, "reasoning_only_agent", lambda task: FakeBaseline())

    monkeypatch.setattr(compare_agents, "reason", fake_reason)

    rows = compare_agents.compare_task({"item": "laptop", "discount": 10, "tax": 18}, expected=849.6)

    baseline = rows[0]
    execution = rows[1]

    assert baseline["correct"] is False
    assert execution["correct"] is True

    assert baseline["tool_calls"] == 0
    assert execution["tool_calls"] == 3
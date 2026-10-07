import pytest
import reasoning_baseline

def test_reasoning_only_agent_without_tools(monkeypatch):
    fake_response = """
    {
        "answer": 844.6,
        "reasoning_note": "Estimated laptop price without tool access."
    }
    """

    monkeypatch.setattr(reasoning_baseline, "call_model", lambda task: fake_response)

    task = {"item": "laptop", "discount": 10, "tax": 18}

    result = reasoning_baseline.reasoning_only_agent(task)

    assert result.agent == "reasoning-only"
    assert result.answer == 844.6
    assert result.tool_calls == 0


def test_reasoning_only_can_be_wrong(monkeypatch):
    fake_response = """
    {
        "answer": 844.6,
        "reasoning_note": "Estimated without checking real price."
    }
    """

    monkeypatch.setattr(reasoning_baseline, "call_model", lambda task: fake_response)

    task = {"item": "laptop", "discount": 10, "tax": 18}

    result = reasoning_baseline.reasoning_only_agent(task)

    real_answer = 849.6

    assert result.answer != real_answer
    assert result.tool_calls == 0

def test_invalid_model_json_is_rejected(monkeypatch):
    monkeypatch.setattr(reasoning_baseline, "call_model", lambda task: "not valid json")

    with pytest.raises(ValueError, match="Model returned invalid JSON"):
        reasoning_baseline.reasoning_only_agent(
            {
                "item": "laptop",
                "discount": 10,
                "tax": 18,
            }
        )


def test_missing_answer_is_rejected(monkeypatch):
    fake_response = """
    {"reasoning_note": "I forgot the answer."}
    """

    monkeypatch.setattr(reasoning_baseline, "call_model", lambda task: fake_response)

    with pytest.raises(ValueError, match="missing answer"):
        reasoning_baseline.reasoning_only_agent({"item": "mouse", "discount": 5, "tax": 10})

def test_non_numeric_answer_is_rejected(monkeypatch):
    fake_response = """
    {
        "answer": "around eight hundred",
        "reasoning_note": "Estimated answer."
    }
    """

    monkeypatch.setattr(reasoning_baseline, "call_model", lambda task: fake_response)

    with pytest.raises(ValueError, match="must be numeric"):
        reasoning_baseline.reasoning_only_agent(
            {
                "item": "laptop",
                "discount": 10,
                "tax": 18,
            }
        )
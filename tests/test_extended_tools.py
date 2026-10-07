import pytest
from extended_tools import add_shipping, execute

def test_add_shipping():
    result = add_shipping(amount=100.0, shipping_fee=10.0)

    assert result == 110.0

def test_add_shipping_in_execution_plan():
    plan = [{"tool": "get_price", "args": ["mouse"]},
            {"tool": "add_shipping", "args": ["$prev", 5]}]

    result, calls = execute(plan)

    assert result == 25.0
    assert calls == 2

def test_negative_shipping_is_rejected():
    with pytest.raises(ValueError, match="shipping fee cannot be negative"):
        add_shipping(amount=100, shipping_fee=-5)

def test_invalid_shipping_type_is_rejected():
    with pytest.raises(ValueError, match="shipping fee must be numeric"):
        add_shipping(amount=100, shipping_fee="five")
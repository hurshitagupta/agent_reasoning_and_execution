import json
import time
from pathlib import Path
from typing import Any

from reasoning_step import reason
from executor import execute
from reasoning_baseline import reasoning_only_agent

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "comparison.json"

def execution_agent(task: dict[str, Any]) -> dict[str, Any]:
    """Reason first, then execute the generated tool plan."""

    start = time.perf_counter()

    plan = reason(task)

    answer, tool_calls = execute(plan)

    seconds = time.perf_counter() - start

    return {
        "agent": "reason+execute",
        "answer": answer,
        "tool_calls": tool_calls,
        "seconds": seconds,
    }


def compare_task(task: dict[str, Any], expected: float) -> list[dict[str, Any]]:
    """Run both agents on the same task and compare their answers against the known expected result."""

    rows = []

    # Reasoning-only agent

    baseline = reasoning_only_agent(task)

    rows.append(
        {
            "agent": baseline.agent,
            "task": task,
            "answer": baseline.answer,
            "expected": expected,
            "correct": baseline.answer == expected,
            "tool_calls": baseline.tool_calls,
            "seconds": round(
                baseline.seconds,
                6,
            ),
        }
    )

    # Reason + execution agent

    executed = execution_agent(task)

    rows.append({
            "agent": executed["agent"],
            "task": task,
            "answer": executed["answer"],
            "expected": expected,
            "correct": executed["answer"] == expected,
            "tool_calls": executed["tool_calls"],
            "seconds": round(executed["seconds"],6)
        })

    return rows


def run_comparison() -> list[dict[str, Any]]:
    """Compare both agents across three pricing tasks."""

    test_cases = [
            {"task": {"item": "laptop", "discount": 10, "tax": 18}, "expected": 849.6},
            {"task": {"item": "mouse", "discount": 5, "tax": 10}, "expected": 20.9},
            {"task": {"item": "keyboard", "discount": 20, "tax": 5},
            "expected": 42.0}]

    results = []

    for case in test_cases:
        comparison = compare_task(task=case["task"], expected=case["expected"])
        results.extend(comparison)

    return results

def save_comparison(results: list[dict[str, Any]],) -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

def print_table(results: list[dict[str, Any]]) -> None:

    print(
        f"{'Agent':<18}"
        f"{'Item':<12}"
        f"{'Answer':<12}"
        f"{'Expected':<12}"
        f"{'Correct':<10}"
        f"{'Calls':<8}"
        f"{'Seconds':<10}"
    )

    print("-" * 82)

    for row in results:
        print(
            f"{row['agent']:<18}"
            f"{row['task']['item']:<12}"
            f"{row['answer']:<12}"
            f"{row['expected']:<12}"
            f"{str(row['correct']):<10}"
            f"{row['tool_calls']:<8}"
            f"{row['seconds']:<10}"
        )


if __name__ == "__main__":

    results = run_comparison()

    print("\n--- AGENT COMPARISON ---\n")

    print_table(results)

    save_comparison(results)

    print(f"\nComparison saved to: {OUTPUT_FILE}")
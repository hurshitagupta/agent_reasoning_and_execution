import json
import os
import time
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from reasoning_step import validate_task

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

@dataclass
class BaselineResult:
    agent: str
    answer: float
    tool_calls: int
    seconds: float
    reasoning_note: str

def call_model(task: dict[str, Any]) -> str:
    """Ask the LLM to estimate the final price without tool access."""

    prompt = f""" You are a reasoning-only pricing agent. You do NOT have access to any tools or real price database.

Task: {json.dumps(task)}

Estimate the final price using your own reasoning. Return ONLY valid JSON in this format:

{{
  "answer": 0.0,
  "reasoning_note": "short explanation"
}}

Rules:
- Do not claim that you called a tool.
- Do not use markdown.
- The answer must be numeric. """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        timeout=3000
    )

    return response.choices[0].message.content

def reasoning_only_agent(task: dict[str, Any]) -> BaselineResult:
    """Produce an answer using only LLM reasoning. No pricing tool is executed."""

    validate_task(task)

    start = time.perf_counter()

    model_output = call_model(task)

    try:
        data = json.loads(model_output)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc

    if "answer" not in data:
        raise ValueError("Model response is missing answer")

    if not isinstance(data["answer"], (int, float)):
        raise ValueError("Model answer must be numeric")

    reasoning_note = data.get("reasoning_note", "No explanation provided")

    seconds = time.perf_counter() - start

    return BaselineResult(
        agent="reasoning-only",
        answer=round(float(data["answer"]), 2),
        tool_calls=0,
        seconds=seconds,
        reasoning_note=str(reasoning_note),
    )

if __name__ == "__main__":

    task = {"item": "laptop", "discount": 10, "tax": 18}

    expected_real_answer = 849.60

    result = reasoning_only_agent(task)

    print("Task:")
    print(task)

    print("\n--- REASONING-ONLY BASELINE ---")

    print(f"Estimated answer: {result.answer}")
    print(f"Tool calls: {result.tool_calls}")
    print(f"Time: {result.seconds:.4f} seconds")
    print(f"Reasoning note: {result.reasoning_note}")

    print("\nExpected tool-backed answer:")
    print(expected_real_answer)

    print("\nCorrect:")
    print(result.answer == expected_real_answer)
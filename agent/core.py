"""마중 Agent Core — 에이전트 루프 (도구 호출 판단 → 실행 → 반영)."""
import ollama

from config import BRAIN_MODEL
from agent.prompts import SYSTEM_PROMPT
from tools.registry import TOOLS, FUNCS


def run_agent(user_text: str, history: list | None = None) -> str:
    """사용자 발화를 받아 두뇌 모델(qwen3:14b)로 도구를 호출하며 답을 만든다.

    LLM이 더 이상 도구를 호출하지 않을 때까지 반복 루프를 돈다.

    Args:
        user_text: 어르신의 입력 텍스트.
        history: 이전 대화 메시지 리스트. 없으면 시스템 프롬프트로 새로 시작.
    Returns:
        최종 답변 텍스트.
    """
    messages = history if history is not None else [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    messages.append({"role": "user", "content": user_text})

    while True:
        resp = ollama.chat(BRAIN_MODEL, messages=messages, tools=TOOLS)
        messages.append(resp.message)

        calls = resp.message.tool_calls
        if not calls:
            return resp.message.content

        for c in calls:
            fn = FUNCS.get(c.function.name)
            try:
                result = fn(**c.function.arguments) if fn else "알 수 없는 도구입니다."
            except Exception as e:  # noqa: BLE001 — 루프를 죽이지 않고 LLM에 실패를 전달
                result = f"도구 실행 중 오류: {e}"
            messages.append({
                "role": "tool",
                "tool_name": c.function.name,
                "content": str(result),
            })

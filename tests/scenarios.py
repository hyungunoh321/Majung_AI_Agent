"""시연 시나리오 자동 테스트.

Phase 1: 시나리오 1(복지 추천)만 검증.
실행: python tests/scenarios.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.prompts import SYSTEM_PROMPT  # noqa: E402
from tools import welfare  # noqa: E402
import tools.registry as registry  # noqa: E402


def test_welfare_recommendation() -> bool:
    """시나리오 1: 도구 호출 여부 + 답변 생성 확인."""
    # 도구 호출 추적 (TOOLS 스키마는 건드리지 않고 실행 함수만 래핑)
    calls: list[dict] = []
    orig = welfare.search_welfare_services

    def traced(**kwargs):
        calls.append(kwargs)
        return orig(**kwargs)

    registry.FUNCS["search_welfare_services"] = traced

    # core 는 import 시점에 FUNCS 를 바인딩하므로 패치 후 import
    from agent.core import run_agent

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    answer = run_agent("파주 사는데 돌봄 서비스 있어요?", history)

    print("=== 도구 호출 ===")
    for c in calls:
        print(c)
    print("\n=== 답변 ===")
    print(answer)

    ok = len(calls) > 0 and bool(answer and answer.strip())
    print("\n=== 결과 ===")
    print("PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if test_welfare_recommendation() else 1)

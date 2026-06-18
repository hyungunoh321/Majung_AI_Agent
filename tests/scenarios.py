"""시연 시나리오 자동 테스트.

각 질문이 의도한 도구를 정확히 호출하는지 검증한다(Phase 2 완료 기준).
실행: python tests/scenarios.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.prompts import SYSTEM_PROMPT  # noqa: E402
import tools.registry as registry  # noqa: E402

# (질문, 기대 도구명) — 세 시나리오가 각각 다른 도구를 써야 한다.
SCENARIOS = [
    ("저 경기도 파주시에 사는데 받을 수 있는 복지 혜택 있을까요?", "search_welfare_services"),
    ("경기도 파주시인데 근처에 경로당이나 데이케어센터 어디 있어요?", "find_welfare_facility"),
    ("경기도 파주시에 노인 일자리 있을까요?", "search_senior_jobs"),
]


def _wrap_tools_with_tracer(calls: list[str]):
    """FUNCS 의 각 도구를 호출 추적 래퍼로 감싼다(스키마용 TOOLS 는 건드리지 않음)."""
    for name, fn in list(registry.FUNCS.items()):
        def make(n, f):
            def traced(**kwargs):
                calls.append(n)
                return f(**kwargs)
            return traced
        registry.FUNCS[name] = make(name, fn)


def main() -> bool:
    calls: list[str] = []
    _wrap_tools_with_tracer(calls)

    # core 는 import 시점에 FUNCS 를 바인딩하므로 패치 후 import
    from agent.core import run_agent  # noqa: E402

    all_ok = True
    for question, expected_tool in SCENARIOS:
        calls.clear()
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        answer = run_agent(question, history)

        called_expected = expected_tool in calls
        has_answer = bool(answer and answer.strip())
        ok = called_expected and has_answer
        all_ok = all_ok and ok

        print(f"\n[{'PASS' if ok else 'FAIL'}] {question}")
        print(f"  기대 도구: {expected_tool}")
        print(f"  실제 호출: {calls or '(없음)'}")
        print(f"  답변 일부: {(answer or '').strip()[:80]}...")

    print("\n=== 최종 결과 ===")
    print("ALL PASS" if all_ok else "SOME FAILED")
    return all_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

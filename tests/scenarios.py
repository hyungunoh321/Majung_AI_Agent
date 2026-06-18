"""시연 시나리오 자동 테스트.

- 시나리오 1·3·노인일자리: 질문별로 올바른 도구를 호출하는지(Phase 2).
- 시나리오 2(서류 해석): 샘플 안내문 이미지 → 비전 추출 → 두뇌 설명(Phase 3).
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


def test_routing(run_agent) -> bool:
    """Phase 2: 질문별 도구 라우팅 검증."""
    calls: list[str] = []
    _wrap_tools_with_tracer(calls)

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

    return all_ok


def test_vision(run_agent) -> bool:
    """Phase 3 시나리오 2: 샘플 안내문 → 비전 추출 → 두뇌 설명."""
    from multimodal.vision import read_document
    from tests.make_sample_doc import make_sample, SAMPLE_PATH

    if not SAMPLE_PATH.exists():
        make_sample()

    print(f"\n[시나리오 2] 서류 해석 — {SAMPLE_PATH.name}")
    extracted = read_document(str(SAMPLE_PATH))
    print(f"  추출 텍스트 일부: {extracted.strip()[:120]}...")

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_text = (
        "어르신이 보여주신 서류 내용입니다:\n"
        f"{extracted}\n\n"
        "이 서류가 무슨 내용인지, 신청 자격과 기한을 어르신께 쉽게 설명해 주세요."
    )
    answer = run_agent(user_text, history) or ""
    print(f"  답변 일부: {answer.strip()[:120]}...")

    # 핵심어가 답변/추출문에 포함되는지(자격·기한 설명) 느슨하게 확인
    blob = (extracted + answer)
    keywords_ok = any(k in blob for k in ("65", "기한", "기간", "신청", "자격"))
    ok = bool(extracted.strip()) and bool(answer.strip()) and keywords_ok
    print(f"  [{'PASS' if ok else 'FAIL'}]")
    return ok


def main() -> bool:
    # core 는 import 시점에 FUNCS 를 바인딩하므로 트레이서 패치 후 import
    from agent.core import run_agent  # noqa: E402

    routing_ok = test_routing(run_agent)
    vision_ok = test_vision(run_agent)
    all_ok = routing_ok and vision_ok

    print("\n=== 최종 결과 ===")
    print(f"  라우팅(Phase 2): {'PASS' if routing_ok else 'FAIL'}")
    print(f"  서류해석(Phase 3): {'PASS' if vision_ok else 'FAIL'}")
    print("ALL PASS" if all_ok else "SOME FAILED")
    return all_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

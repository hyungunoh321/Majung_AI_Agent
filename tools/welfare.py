"""① 복지서비스 검색 도구 (중앙부처복지서비스 카탈로그).

Phase 1~2: data/mock/welfare.json 의 고정 데이터를 읽어 반환.
Phase 4: DATA_GO_KR_KEY 로 실제 오픈API 호출로 교체.
"""
import json

from config import USE_MOCK, MOCK_DIR


def _fetch_welfare(region: str, keyword: str) -> list[dict]:
    """mock 또는 실제 API 에서 복지 서비스 후보를 가져온다 (내부용)."""
    if USE_MOCK:
        with open(MOCK_DIR / "welfare.json", encoding="utf-8") as f:
            data = json.load(f)
        # 지역(전국 포함)과 키워드로 느슨하게 필터링
        items = []
        for x in data:
            region_ok = (
                not region
                or "전국" in x["regions"]
                or any(region in r or r in region for r in x["regions"])
            )
            keyword_ok = (
                not keyword
                or any(keyword in k or k in keyword for k in x["keywords"])
                or keyword in x["name"]
            )
            if region_ok and keyword_ok:
                items.append(x)
        return items
    # Phase 4 에서 실제 API 호출 구현
    raise NotImplementedError("실제 API 호출은 Phase 4 에서 구현합니다.")


def search_welfare_services(region: str, keyword: str) -> str:
    """신청해서 받는 노인복지 제도·혜택·지원금을 검색합니다.

    기초연금, 돌봄 서비스, 장기요양보험, 각종 지원금처럼 '제도/프로그램'을 찾을 때
    사용합니다. (특정 건물·장소의 위치를 찾는 것이 아니라, 받을 수 있는 혜택을 찾는 도구)

    Args:
        region: 거주 지역 (예: '경기도 파주시')
        keyword: 관심 분야 (예: '돌봄', '기초연금', '장기요양', '지원금')
    Returns:
        복지 서비스 후보 요약 (서비스명 / 지원대상 / 신청방법)
    """
    items = _fetch_welfare(region, keyword)
    if not items:
        return f"'{keyword}' 관련 서비스를 찾지 못했습니다."
    return "\n".join(
        f"- {x['name']}: 대상 {x['target']} / 신청 {x['how']}" for x in items[:5]
    )

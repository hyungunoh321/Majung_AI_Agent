"""③ 노인 일자리·사회활동 지원사업 도구.

Phase 2: data/mock/jobs.json 의 고정 데이터를 읽어 반환.
Phase 4: data/노인일자리_사업.csv 를 pandas 로 읽어 지역(시도)별 요약으로 교체.
"""
import json

from config import USE_MOCK, MOCK_DIR


def _fetch_jobs(region: str) -> list[dict]:
    """mock 또는 실제 csv 에서 노인일자리 후보를 가져온다 (내부용)."""
    if USE_MOCK:
        with open(MOCK_DIR / "jobs.json", encoding="utf-8") as f:
            data = json.load(f)
        items = []
        for x in data:
            region_ok = (
                not region
                or "전국" in x["regions"]
                or any(region in r or r in region for r in x["regions"])
            )
            if region_ok:
                items.append(x)
        return items
    # Phase 4 에서 csv 로딩 구현
    raise NotImplementedError("실제 csv 연결은 Phase 4 에서 구현합니다.")


def search_senior_jobs(region: str) -> str:
    """어르신 거주지에서 참여할 수 있는 노인 일자리·사회활동 사업을 찾습니다.

    Args:
        region: 거주 지역 (예: '경기도 파주시')
    Returns:
        노인 일자리 사업 요약 (사업명 / 참여대상 / 신청방법)
    """
    items = _fetch_jobs(region)
    if not items:
        return f"'{region}'에서 참여 가능한 노인 일자리 사업을 찾지 못했습니다."
    return "\n".join(
        f"- {x['name']}: 대상 {x['target']} / 신청 {x['how']}" for x in items[:5]
    )

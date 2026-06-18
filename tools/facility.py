"""④+② 복지시설/장기요양기관 찾기 도구.

Phase 2: data/mock/facility.json 의 고정 데이터를 읽어 반환.
Phase 4: ④오픈API(전국사회복지시설 표준데이터) + ②xlsx(노인장기요양기관 현황) 조합으로 교체.
"""
import json

from config import USE_MOCK, MOCK_DIR


def _fetch_facility(region: str, kind: str) -> list[dict]:
    """mock 또는 실제 데이터에서 시설 후보를 가져온다 (내부용)."""
    if USE_MOCK:
        with open(MOCK_DIR / "facility.json", encoding="utf-8") as f:
            data = json.load(f)
        items = []
        for x in data:
            region_ok = (
                not region
                or "전국" in x["regions"]
                or any(region in r or r in region for r in x["regions"])
            )
            kind_ok = not kind or kind in x["kind"] or x["kind"] in kind
            if region_ok and kind_ok:
                items.append(x)
        return items
    # Phase 4 에서 ④API + ②xlsx 조합 구현
    raise NotImplementedError("실제 API/파일 연결은 Phase 4 에서 구현합니다.")


def find_welfare_facility(region: str, kind: str) -> str:
    """어르신이 직접 갈 수 있는 복지시설의 위치와 연락처를 찾습니다.

    경로당, 주간보호센터(데이케어), 요양원처럼 '실제 건물·장소'가 어디 있는지,
    주소와 전화번호를 알고 싶을 때 사용합니다. (제도·혜택을 찾는 도구가 아님)

    Args:
        region: 거주 지역 (예: '경기도 파주시')
        kind: 시설 종류. '경로당', '데이케어'(주간보호센터), '장기요양기관'(요양원·방문요양) 중 하나.
    Returns:
        시설 후보 요약 (시설명 / 주소 / 전화번호)
    """
    items = _fetch_facility(region, kind)
    if not items:
        return f"'{region}' 근처에서 '{kind}' 시설을 찾지 못했습니다."
    return "\n".join(
        f"- {x['name']}: {x['address']} / 전화 {x['phone']}" for x in items[:5]
    )

"""②(+④) 복지시설/장기요양기관 찾기 도구.

USE_MOCK=true : data/mock/facility.json 의 고정 데이터.
USE_MOCK=false: data/노인장기요양기관_현황.xlsx 를 우선 사용(이름·주소).
  - 파일에 전화번호·시설종류 컬럼이 없어, 전화번호는 생략하고 종류는 이름 키워드로 추정한다.
  - ④ 전국사회복지시설표준데이터 API 는 공개 오퍼레이션이 사업자번호 조회 위주라
    지역·이름 기반 보강이 어려워 best-effort(미지원 시 조용히 생략)로 둔다.
"""
import json
from functools import lru_cache

import pandas as pd

from config import USE_MOCK, MOCK_DIR, LTC_XLSX

# 이름으로 종류를 추정하기 위한 키워드
_KIND_KEYWORDS = {
    "데이케어": ("주간보호", "데이케어", "주야간"),
    "주간보호": ("주간보호", "데이케어", "주야간"),
}


@lru_cache(maxsize=1)
def _load_ltc_df() -> pd.DataFrame:
    """장기요양기관 현황 xlsx 를 1회만 읽어 캐싱한다."""
    return pd.read_excel(LTC_XLSX)


def _region_tokens(region: str) -> list[str]:
    """'경기도 파주시' → ['경기도','파주시'] 중 의미있는(2자 이상) 토큰만."""
    return [t for t in region.split() if len(t) >= 2]


def _fetch_facility_mock(region: str, kind: str) -> list[dict]:
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


def _fetch_facility_real(region: str, kind: str) -> list[dict]:
    """실제 xlsx 에서 지역/종류로 필터링한 시설 목록(이름·주소)."""
    # 경로당 등 장기요양기관 파일에 없는 종류는 빈 목록 → 호출부에서 안내 처리
    if kind and "경로당" in kind:
        return []

    df = _load_ltc_df()
    addr = df["기관별 상세주소"].astype(str)
    tokens = _region_tokens(region)
    if tokens:
        mask = addr.str.contains(tokens[-1], na=False)  # 가장 구체적인 시/군/구 토큰
        df = df[mask]

    keywords = _KIND_KEYWORDS.get(kind)
    if keywords:
        name = df["장기요양기관이름"].astype(str)
        df = df[name.str.contains("|".join(keywords), na=False)]

    items = []
    for _, row in df.head(5).iterrows():
        items.append({
            "name": str(row["장기요양기관이름"]).strip(),
            "address": str(row["기관별 상세주소"]).strip(),
            "phone": None,  # 파일에 전화번호 없음
        })
    return items


def _format(items: list[dict]) -> str:
    lines = []
    for x in items:
        phone = x.get("phone")
        tail = f" / 전화 {phone}" if phone else ""
        lines.append(f"- {x['name']}: {x['address']}{tail}")
    return "\n".join(lines)


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
    if USE_MOCK:
        items = _fetch_facility_mock(region, kind)
    else:
        items = _fetch_facility_real(region, kind)

    if not items:
        if not USE_MOCK and kind and "경로당" in kind:
            return (
                f"'{region}' 경로당 위치는 동네 주민센터에 문의하시면 가장 정확합니다. "
                "보건복지상담센터(전화 129)로도 안내받으실 수 있어요."
            )
        return f"'{region}' 근처에서 '{kind}' 시설을 찾지 못했습니다."
    return _format(items)

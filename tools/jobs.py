"""③ 노인 일자리·사회활동 지원사업 도구.

USE_MOCK=true : data/mock/jobs.json 의 고정 데이터를 읽어 반환.
USE_MOCK=false: data/노인일자리_사업.csv(cp949, 시도 단위 통계)를 읽어 최신연도 규모 요약.
"""
import json
from functools import lru_cache

import pandas as pd

from config import USE_MOCK, MOCK_DIR, JOBS_CSV

# 입력 지역 문자열에서 찾아낼 시도(광역) 한글 토큰. csv의 '시도' 컬럼은 '경기 Gyeonggi' 형식.
_SIDO_TOKENS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]


@lru_cache(maxsize=1)
def _load_jobs_df() -> pd.DataFrame:
    """노인일자리 csv 를 1회만 읽어 캐싱한다(cp949 인코딩)."""
    return pd.read_csv(JOBS_CSV, encoding="cp949")


def _region_to_sido(region: str) -> str | None:
    """'경기도 파주시' 같은 입력에서 시도 토큰('경기')을 찾아낸다."""
    for token in _SIDO_TOKENS:
        if token in region:
            return token
    return None


def _fetch_jobs_mock(region: str) -> list[dict]:
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


def _fetch_jobs_real(region: str) -> str:
    """실제 csv 에서 해당 시도의 최신연도 참여 규모를 요약 텍스트로 반환한다."""
    df = _load_jobs_df()
    sido = _region_to_sido(region)
    if sido is None:
        return "지역을 알기 어려워요. '경기도 파주시'처럼 시·도를 포함해 말씀해 주세요."

    sub = df[df["시도"].astype(str).str.contains(sido)]
    if sub.empty:
        return f"'{region}' 지역의 노인일자리 통계를 찾지 못했습니다."

    latest_year = int(sub["연도"].max())
    row = sub[sub["연도"] == latest_year].iloc[0]
    return (
        f"{sido} 지역 노인일자리 참여 규모({latest_year}년 기준)\n"
        f"- 공공형(공익활동): 약 {int(row['공공형']):,}명\n"
        f"- 사회서비스형: 약 {int(row['사회서비스형']):,}명\n"
        f"- 민간형(시장·취업): 약 {int(row['민간형']):,}명\n"
        f"신청: 가까운 시니어클럽·노인복지관 또는 주민센터에 문의하세요."
    )


def search_senior_jobs(region: str) -> str:
    """어르신 거주지에서 참여할 수 있는 노인 일자리·사회활동 사업을 찾습니다.

    Args:
        region: 거주 지역 (예: '경기도 파주시')
    Returns:
        노인 일자리 사업·참여 규모 요약과 신청 방법.
    """
    if not USE_MOCK:
        return _fetch_jobs_real(region)

    items = _fetch_jobs_mock(region)
    if not items:
        return f"'{region}'에서 참여 가능한 노인 일자리 사업을 찾지 못했습니다."
    return "\n".join(
        f"- {x['name']}: 대상 {x['target']} / 신청 {x['how']}" for x in items[:5]
    )

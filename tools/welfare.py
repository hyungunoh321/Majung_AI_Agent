"""① 복지서비스 검색 도구 (중앙부처복지서비스 카탈로그).

USE_MOCK=true : data/mock/welfare.json 의 고정 데이터를 읽어 반환.
USE_MOCK=false: DATA_GO_KR_KEY 로 data.go.kr ① 오픈API(목록조회) 호출 후 요약.
"""
import json
import xml.etree.ElementTree as ET

import requests

from config import USE_MOCK, MOCK_DIR, WELFARE_API_URL, DATA_GO_KR_KEY


def _fetch_welfare_mock(region: str, keyword: str) -> list[dict]:
    with open(MOCK_DIR / "welfare.json", encoding="utf-8") as f:
        data = json.load(f)
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


def _fetch_welfare_api(keyword: str) -> list[dict]:
    """① 중앙부처복지서비스 목록조회 API 를 호출해 요약 dict 리스트로 변환한다."""
    params = {
        "serviceKey": DATA_GO_KR_KEY,
        "callTp": "L",
        "pageNo": "1",
        "numOfRows": "10",
        "srchKeyCode": "001",   # 001 = 키워드(텍스트) 검색
        "searchWrd": keyword or "노인",
    }
    resp = requests.get(WELFARE_API_URL, params=params, timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    code = root.findtext("resultCode")
    if code not in ("0", "00"):
        msg = root.findtext("resultMessage") or "알 수 없는 오류"
        raise RuntimeError(f"복지서비스 API 오류({code}): {msg}")

    items = []
    for serv in root.iter("servList"):
        name = (serv.findtext("servNm") or "").strip()
        if not name:
            continue
        target = (serv.findtext("trgterIndvdlArray") or "").strip() or "어르신(노년)"
        contact = (serv.findtext("rprsCtadr") or "").strip()
        online = (serv.findtext("onapPsbltYn") or "").strip() == "Y"
        how = f"문의 {contact}" if contact else "주민센터·복지로(129) 문의"
        if online:
            how += ", 온라인 신청 가능(복지로)"
        items.append({"name": name, "target": target, "how": how})
    return items


def _fetch_welfare(region: str, keyword: str) -> list[dict]:
    """mock 또는 실제 API 에서 복지 서비스 후보를 가져온다 (내부용)."""
    if USE_MOCK:
        return _fetch_welfare_mock(region, keyword)
    return _fetch_welfare_api(keyword)


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

"""① 복지서비스 검색 + 신청 페이지 안내 도구.

USE_MOCK=true : data/mock/welfare.json 의 고정 데이터를 읽어 반환.
USE_MOCK=false: DATA_GO_KR_KEY 로 data.go.kr ① 오픈API(목록조회) 호출 후 요약.

검색 결과에는 복지로 '신청 페이지 링크'가 포함되며, 어르신이 신청을 원하면
open_welfare_application() 으로 그 페이지를 브라우저로 열어 드린다.
(실제 신청·본인인증·제출은 어르신이 직접 — 법적 효력이 있는 단계라 대신하지 않는다.)
"""
import json
import webbrowser
import xml.etree.ElementTree as ET

import requests

from config import USE_MOCK, MOCK_DIR, WELFARE_API_URL, DATA_GO_KR_KEY

# 최근 검색에서 얻은 '서비스명 → 신청 페이지 링크' 캐시 (open 도구가 참조).
_recent_links: dict[str, str] = {}


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
            items.append({
                "name": x["name"],
                "target": x["target"],
                "how": x["how"],
                "link": x.get("link", ""),
            })
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
        link = (serv.findtext("servDtlLink") or "").strip()
        how = f"문의 {contact}" if contact else "주민센터·복지로(129) 문의"
        if online:
            how += ", 온라인 신청 가능(복지로)"
        items.append({"name": name, "target": target, "how": how, "link": link})
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
        복지 서비스 후보 요약 (서비스명 / 지원대상 / 신청방법 / 신청 페이지 링크)
    """
    items = _fetch_welfare(region, keyword)
    if not items:
        return f"'{keyword}' 관련 서비스를 찾지 못했습니다."

    lines = []
    for x in items[:5]:
        if x.get("link"):
            _recent_links[x["name"]] = x["link"]
        line = f"- {x['name']}: 대상 {x['target']} / 신청 {x['how']}"
        if x.get("link"):
            line += f"\n  신청 페이지: {x['link']}"
        lines.append(line)
    return "\n".join(lines)


def open_welfare_application(service_name: str) -> str:
    """어르신이 신청을 원하는 복지서비스의 신청 페이지를 웹 브라우저로 열어 드립니다.

    바로 직전 검색에서 찾은 복지서비스의 복지로 신청 페이지를 띄웁니다.
    (실제 신청서 작성·본인인증·제출은 어르신이 직접 하셔야 합니다.)

    Args:
        service_name: 신청을 원하는 복지서비스 이름 (예: '기초연금').
    Returns:
        페이지를 열었는지 여부와 안내 메시지.
    """
    if not _recent_links:
        return "먼저 어떤 복지가 있는지 찾아본 뒤에 신청 페이지를 열 수 있어요."

    # 이름 부분 일치로 가장 알맞은 링크를 찾는다.
    match = None
    for name, url in _recent_links.items():
        if service_name in name or name in service_name:
            match = (name, url)
            break
    if match is None:
        names = ", ".join(_recent_links)
        return f"'{service_name}'에 해당하는 신청 페이지를 못 찾았어요. 찾은 서비스: {names}"

    name, url = match
    try:
        webbrowser.open(url)
    except Exception as e:  # noqa: BLE001
        return f"'{name}' 신청 페이지 주소는 {url} 인데, 브라우저를 여는 데 실패했어요({e})."
    return (
        f"'{name}' 신청 페이지를 열었습니다: {url}\n"
        "화면에서 본인인증을 하신 뒤 신청을 진행하시면 됩니다. 옆에서 도와드릴게요."
    )

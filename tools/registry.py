"""도구 레지스트리 — TOOLS(함수 리스트) + FUNCS(이름→함수 매핑).

Phase 1: search_welfare_services 1종.
Phase 2 에서 facility / jobs 도구를 추가한다.
"""
from tools.welfare import search_welfare_services

# ollama 가 타입힌트+docstring 으로 스키마를 자동 생성한다.
TOOLS = [
    search_welfare_services,
]

FUNCS = {fn.__name__: fn for fn in TOOLS}

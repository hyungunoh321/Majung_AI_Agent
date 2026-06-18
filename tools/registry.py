"""도구 레지스트리 — TOOLS(함수 리스트) + FUNCS(이름→함수 매핑).

Phase 2: search_welfare_services / find_welfare_facility / search_senior_jobs 3종.
"""
from tools.welfare import search_welfare_services
from tools.facility import find_welfare_facility
from tools.jobs import search_senior_jobs

# ollama 가 타입힌트+docstring 으로 스키마를 자동 생성한다.
TOOLS = [
    search_welfare_services,
    find_welfare_facility,
    search_senior_jobs,
]

FUNCS = {fn.__name__: fn for fn in TOOLS}

"""마중 프로젝트 설정 — 모델명, 상수, 키 로딩."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 모델 (확정 — 변경 금지)
BRAIN_MODEL = "qwen3:14b"     # 대화·추론·도구 호출 담당 두뇌
VISION_MODEL = "gemma3:12b"   # 이미지/서류 OCR 전용

# Ollama 서버
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# data.go.kr 오픈API 인증키 (①·④) — .env 에서만 로드
DATA_GO_KR_KEY = os.getenv("DATA_GO_KR_KEY", "")

# 개발 단계 토글: true=mock 데이터, false=실제 파일+API
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# 경로
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MOCK_DIR = DATA_DIR / "mock"

# ②·③ 로컬 데이터 파일 경로
LTC_XLSX = DATA_DIR / "노인장기요양기관_현황.xlsx"   # ② 장기요양
JOBS_CSV = DATA_DIR / "노인일자리_사업.csv"          # ③ 노인일자리

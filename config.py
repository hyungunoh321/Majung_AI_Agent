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

# data.go.kr 오픈API 엔드포인트
# ① 중앙부처복지서비스 (목록 조회)
WELFARE_API_URL = (
    "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001"
    "/NationalWelfarelistV001"
)
# ④ 전국사회복지시설표준데이터 (best-effort)
FACILITY_API_BASE = "http://apis.data.go.kr/B554287/sclWlfrFcltInfoInqirService1"

# 음성 (Phase 5)
STT_MODEL_SIZE = "small"      # faster-whisper 모델 크기 (CPU 실행 기준 균형)
STT_DEVICE = "cpu"            # AMD GPU는 CTranslate2 가속 불가 → CPU
STT_COMPUTE_TYPE = "int8"     # CPU에서 가볍고 빠른 양자화
TTS_VOICE = "ko-KR-SunHiNeural"   # edge-tts 한국어 여성 음성

# 경로
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MOCK_DIR = DATA_DIR / "mock"

# ②·③ 로컬 데이터 파일 경로
LTC_XLSX = DATA_DIR / "노인장기요양기관_현황.xlsx"   # ② 장기요양
JOBS_CSV = DATA_DIR / "노인일자리_사업.csv"          # ③ 노인일자리

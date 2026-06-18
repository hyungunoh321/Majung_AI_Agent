"""테스트용 샘플 복지 안내문 이미지를 생성한다.

실행: python tests/make_sample_doc.py
결과: data/sample/안내문_샘플.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from config import DATA_DIR  # noqa: E402

SAMPLE_PATH = DATA_DIR / "sample" / "안내문_샘플.png"

# 안내문에 들어갈 내용 (제도명 / 대상 / 기한 / 문의처)
LINES = [
    ("기초연금 신청 안내", 40, True),
    ("", 12, False),
    ("○ 제도명: 기초연금", 28, False),
    ("○ 신청 자격: 만 65세 이상이고 소득과 재산이", 28, False),
    ("   일정 기준 이하인 어르신", 28, False),
    ("○ 신청 기간: 2026년 7월 1일 ~ 7월 31일", 28, False),
    ("○ 신청 장소: 가까운 주민센터 또는 국민연금공단", 28, False),
    ("○ 문의처: 파주시청 노인복지과 (031-940-0000)", 28, False),
    ("", 12, False),
    ("※ 신청은 본인 또는 대리인이 할 수 있습니다.", 24, False),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """맑은 고딕 폰트를 불러온다(없으면 기본 폰트 폴백)."""
    for path in (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_sample() -> Path:
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    width, height = 900, 560
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # 테두리
    draw.rectangle([20, 20, width - 20, height - 20], outline="black", width=3)

    y = 50
    for text, size, bold in LINES:
        font = _load_font(size)
        x = 60 if not bold else (width - draw.textlength(text, font=font)) / 2
        draw.text((x, y), text, fill="black", font=font)
        y += size + 16

    img.save(SAMPLE_PATH)
    return SAMPLE_PATH


if __name__ == "__main__":
    path = make_sample()
    print(f"샘플 안내문 생성: {path}")

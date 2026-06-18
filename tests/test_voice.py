"""음성 라운드트립 검증 (마이크 없이 STT+TTS 동시 확인).

edge-tts 로 한국어 mp3 를 만든 뒤 faster-whisper 로 다시 인식해,
원문 핵심어가 인식문에 포함되는지로 PASS 를 판정한다.
실행: python tests/test_voice.py
"""
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from multimodal.tts import _synthesize  # noqa: E402
from multimodal.stt import transcribe  # noqa: E402

SENTENCE = "안녕하세요. 마중 음성 테스트입니다."
KEYWORDS = ("마중", "안녕", "테스트")


def main() -> bool:
    mp3 = Path(tempfile.gettempdir()) / "majung_voice_test.mp3"

    print("1) edge-tts 로 음성 합성 중...")
    _synthesize(SENTENCE, str(mp3))
    ok_tts = mp3.exists() and mp3.stat().st_size > 0
    print(f"   합성 파일: {mp3} ({mp3.stat().st_size if mp3.exists() else 0} bytes)")

    print("2) faster-whisper 로 음성 인식 중... (첫 실행 시 모델 다운로드)")
    recognized = transcribe(str(mp3))
    print(f"   원문 : {SENTENCE}")
    print(f"   인식 : {recognized}")

    hit = any(k in recognized for k in KEYWORDS)
    ok = ok_tts and bool(recognized.strip()) and hit

    print("\n=== 결과 ===")
    print(f"  TTS 합성: {'PASS' if ok_tts else 'FAIL'}")
    print(f"  STT 인식(핵심어 포함): {'PASS' if hit else 'FAIL'}")
    print("ALL PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

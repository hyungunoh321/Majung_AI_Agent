"""음성 → 텍스트 (STT) — faster-whisper.

명세서 5-4 인터페이스: transcribe(audio_path) -> str.
마이크 녹음 헬퍼 record_microphone(seconds) -> wav 경로 도 함께 제공한다.
AMD GPU는 CTranslate2 가속 대상이 아니므로 CPU(int8)로 동작한다.
"""
from functools import lru_cache
from pathlib import Path
import tempfile

from config import STT_MODEL_SIZE, STT_DEVICE, STT_COMPUTE_TYPE


@lru_cache(maxsize=1)
def _get_model():
    """faster-whisper 모델을 1회만 로드해 캐싱한다(첫 호출 시 다운로드)."""
    from faster_whisper import WhisperModel
    return WhisperModel(STT_MODEL_SIZE, device=STT_DEVICE, compute_type=STT_COMPUTE_TYPE)


def transcribe(audio_path: str) -> str:
    """음성 파일(wav/mp3 등)을 한국어 텍스트로 변환한다.

    Args:
        audio_path: 인식할 오디오 파일 경로.
    Returns:
        인식된 텍스트. 실패 시 사람이 읽을 수 있는 안내 문자열.
    """
    if not Path(audio_path).is_file():
        return f"음성 파일을 찾지 못했습니다: {audio_path}"
    try:
        model = _get_model()
        segments, _info = model.transcribe(audio_path, language="ko", beam_size=5)
        return "".join(seg.text for seg in segments).strip()
    except Exception as e:  # noqa: BLE001 — STT 실패가 전체 흐름을 끊지 않게 함
        return f"음성을 알아듣지 못했습니다: {e}"


def record_microphone(seconds: int = 5, samplerate: int = 16000) -> str:
    """마이크로 일정 시간 녹음해 임시 wav 파일로 저장하고 경로를 반환한다.

    Args:
        seconds: 녹음 길이(초).
        samplerate: 샘플링 레이트(Whisper 권장 16kHz).
    Returns:
        저장된 wav 파일 경로. 마이크 오류 시 빈 문자열.
    """
    try:
        import sounddevice as sd
        import soundfile as sf

        print(f"🎤 {seconds}초 동안 말씀해 주세요...")
        audio = sd.rec(int(seconds * samplerate), samplerate=samplerate,
                       channels=1, dtype="int16")
        sd.wait()
        out = Path(tempfile.gettempdir()) / "majung_record.wav"
        sf.write(str(out), audio, samplerate)
        print("🎤 녹음이 끝났습니다.")
        return str(out)
    except Exception as e:  # noqa: BLE001
        print(f"마이크 녹음에 실패했습니다: {e}")
        return ""

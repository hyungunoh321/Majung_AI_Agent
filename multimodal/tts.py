"""텍스트 → 음성 (TTS) — edge-tts (한국어).

명세서 5-4 인터페이스: speak(text) -> None.
edge-tts(온라인)로 mp3를 만들어 재생한다. 재생 실패 시 텍스트를 print 하여
파이프라인이 끊기지 않게 한다(스텁 철학 유지).
"""
import asyncio
import os
from pathlib import Path
import re
import tempfile

from config import TTS_VOICE


def _clean_for_speech(text: str) -> str:
    """마크다운 기호를 지워 음성이 '별표'·'우물 정' 등을 읽지 않게 한다."""
    # **굵게**, *기울임*, `코드`, ~~취소선~~ 등의 강조 기호 제거 (안쪽 글자는 보존)
    text = re.sub(r"[*_`~]+", "", text)
    # 줄머리 기호: '- ', '* ', '+ ', '#', '>' (목록·제목·인용)
    text = re.sub(r"(?m)^\s*[-*+#>]+\s*", "", text)
    # 1. 2. 같은 번호 목록은 어르신께 순서로 읽어주는 게 좋아 유지한다.
    return text.strip()


def _synthesize(text: str, out_path: str) -> None:
    """edge-tts 로 text 를 mp3 로 합성한다(비동기 내부 실행)."""
    import edge_tts

    async def _run():
        communicate = edge_tts.Communicate(text, TTS_VOICE)
        await communicate.save(out_path)

    asyncio.run(_run())


def _play(path: str) -> bool:
    """mp3 파일을 재생한다. 성공 여부를 반환."""
    try:
        from playsound import playsound  # 있으면 사용
        playsound(path)
        return True
    except Exception:
        pass
    try:
        os.startfile(path)  # Windows 기본 플레이어 폴백
        return True
    except Exception:
        return False


def speak(text: str) -> None:
    """답변 텍스트를 한국어 음성으로 들려준다.

    Args:
        text: 읽어 줄 텍스트.
    """
    if not text or not text.strip():
        return
    spoken = _clean_for_speech(text)
    if not spoken:
        return
    try:
        out = Path(tempfile.gettempdir()) / "majung_tts.mp3"
        _synthesize(spoken, str(out))
        if not _play(str(out)):
            print(f"[음성 재생 실패 — 텍스트로 안내] {text}")
    except Exception as e:  # noqa: BLE001 — TTS 실패가 전체 흐름을 끊지 않게 함
        print(f"[음성 합성 실패 — 텍스트로 안내] {text}\n(원인: {e})")

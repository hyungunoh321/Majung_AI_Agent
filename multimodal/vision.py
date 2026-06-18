"""서류 인식(비전) — gemma3:12b 로 이미지에서 핵심 정보를 텍스트로 추출.

명세서 6장 규칙: 이 모듈은 gemma3 만 호출하고, 추출 결과(텍스트)는 두뇌(qwen3,
agent.core.run_agent)로 넘긴다. 두 모델 호출을 한 번에 섞지 않는다.
"""
import os

import ollama

from config import VISION_MODEL

_PROMPT = (
    "이 문서에서 제도명·신청 자격·신청 기한·문의처만 뽑아 한국어로 간단히 정리해 주세요. "
    "추측하지 말고 문서에 적힌 내용만 알려 주세요."
)


def read_document(image_path: str) -> str:
    """우편 안내문/신분증 사진에서 핵심 정보를 텍스트로 추출한다.

    Args:
        image_path: 읽을 이미지 파일 경로(.jpg/.png 등).
    Returns:
        제도명·신청 자격·신청 기한·문의처 위주로 정리된 한국어 텍스트.
        실패 시 사람이 읽을 수 있는 오류 안내 문자열.
    """
    if not os.path.isfile(image_path):
        return f"이미지 파일을 찾지 못했습니다: {image_path}"
    try:
        resp = ollama.chat(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": _PROMPT,
                "images": [image_path],
            }],
        )
        return resp.message.content
    except Exception as e:  # noqa: BLE001 — 비전 실패가 전체 흐름을 끊지 않게 함
        return f"서류를 읽는 중 문제가 생겼습니다: {e}"

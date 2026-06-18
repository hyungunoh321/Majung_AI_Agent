"""마중 CLI 진입점 — 터미널 대화 루프."""
import os

from agent.core import run_agent
from agent.prompts import SYSTEM_PROMPT
from multimodal.vision import read_document

_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def _maybe_image_path(text: str) -> str | None:
    """입력이 존재하는 이미지 파일 경로면 그 경로를, 아니면 None 을 돌려준다."""
    path = text.strip().strip('"').strip("'")
    if path.lower().endswith(_IMAGE_EXTS) and os.path.isfile(path):
        return path
    return None


def main() -> None:
    print("=" * 50)
    print(" 마중(Majung) — 어르신 복지 도우미")
    print(" 서류 사진은 이미지 파일 경로를 그대로 입력하세요.")
    print(" 종료하려면 'exit' 또는 '종료' 를 입력하세요.")
    print("=" * 50)

    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_text = input("\n어르신> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n마중> 안녕히 계세요. 또 찾아주세요.")
            break

        if not user_text:
            continue
        if user_text.lower() in ("exit", "quit", "종료"):
            print("마중> 안녕히 계세요. 또 찾아주세요.")
            break

        image_path = _maybe_image_path(user_text)
        if image_path:
            print("마중> 서류를 읽고 있어요. 잠시만 기다려 주세요...")
            extracted = read_document(image_path)
            user_text = (
                "어르신이 보여주신 서류 내용입니다:\n"
                f"{extracted}\n\n"
                "이 서류가 무슨 내용인지, 신청 자격과 기한을 어르신께 쉽게 설명해 주세요."
            )

        answer = run_agent(user_text, history)
        print(f"\n마중> {answer}")


if __name__ == "__main__":
    main()

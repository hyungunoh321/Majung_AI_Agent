"""마중 CLI 진입점 — 터미널 대화 루프."""
import os

from agent.core import run_agent
from agent.prompts import SYSTEM_PROMPT
from multimodal.vision import read_document

_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
_VOICE_CMDS = ("녹음", "음성")
_PHOTO_CMDS = ("사진", "파일", "사진첨부", "사진 첨부")


def _maybe_image_path(text: str) -> str | None:
    """입력이 존재하는 이미지 파일 경로면 그 경로를, 아니면 None 을 돌려준다."""
    path = text.strip().strip('"').strip("'")
    if path.lower().endswith(_IMAGE_EXTS) and os.path.isfile(path):
        return path
    return None


def _pick_image_via_dialog() -> str:
    """파일 선택 창을 띄워 어르신이 클릭으로 사진을 고르게 한다. 경로 또는 빈 문자열."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # 창을 맨 앞으로
        path = filedialog.askopenfilename(
            title="서류 사진을 선택하세요",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("모든 파일", "*.*"),
            ],
        )
        root.destroy()
        return path or ""
    except Exception as e:  # noqa: BLE001 — 창을 못 띄우면 경로 입력으로 안내
        print(f"(파일 선택 창을 열 수 없어요: {e} — 사진 파일 경로를 직접 입력해 주세요)")
        return ""


def main() -> None:
    print("=" * 50)
    print(" 마중(Majung) — 어르신 복지 도우미")
    print(" 서류 사진을 보여주려면 '사진' 이라고 입력하세요(파일 선택 창이 떠요).")
    print(" 음성으로 말하려면 '녹음' 이라고 입력하세요.")
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

        voice_mode = user_text in _VOICE_CMDS
        if voice_mode:
            # 마이크 녹음 → STT 로 텍스트 변환 (음성 모듈은 필요할 때만 import)
            from multimodal.stt import record_microphone, transcribe
            wav_path = record_microphone(seconds=10)
            if not wav_path:
                continue
            user_text = transcribe(wav_path)
            print(f"어르신(음성)> {user_text}")
            if not user_text.strip():
                continue
        else:
            if user_text in _PHOTO_CMDS:
                image_path = _pick_image_via_dialog()
                if not image_path:
                    print("마중> 사진을 고르지 않으셨어요. 다시 '사진'이라고 말씀해 주세요.")
                    continue
            else:
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

        if voice_mode:
            # 음성으로 들어왔으면 음성으로 답한다
            from multimodal.tts import speak
            speak(answer)


if __name__ == "__main__":
    main()

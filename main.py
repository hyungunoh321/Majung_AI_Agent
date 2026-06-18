"""마중 CLI 진입점 — 터미널 대화 루프."""
from agent.core import run_agent
from agent.prompts import SYSTEM_PROMPT


def main() -> None:
    print("=" * 50)
    print(" 마중(Majung) — 어르신 복지 도우미")
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

        answer = run_agent(user_text, history)
        print(f"\n마중> {answer}")


if __name__ == "__main__":
    main()

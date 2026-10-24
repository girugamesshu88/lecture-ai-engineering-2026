"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保ったまま続けて質問する（宿題：実装）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    # 演習: 入力トークン数と出力トークン数を表示する
    usage = response.usage_metadata
    print(f"[トークン] 入力 {usage.prompt_token_count} / 出力 {usage.candidates_token_count}")

    return response.text


def chat() -> None:
    """会話履歴を保ったまま、続けて質問する。exit か空行で終わる。"""
    client = genai.Client(api_key=get_api_key())
    session = client.chats.create(model=MODEL)  # 履歴を覚えておく「会話」を作る

    print(f"[model] {MODEL}")
    print("会話モード（終わるときは exit か、何も入力せずEnter）\n")
    while True:
        try:
            question = input("あなた> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question in ("", "exit", "quit"):
            break

        try:
            # send_message は、これまでの履歴＋今回の質問をまとめて送ってくれる
            response = session.send_message(question)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            continue

        print(f"AI> {response.text}")
        usage = response.usage_metadata
        print(f"[トークン] 入力 {usage.prompt_token_count} / 出力 {usage.candidates_token_count}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って続けて質問する")
    args = parser.parse_args()

    if args.chat:
        chat()
        return

    print(f"[model] {MODEL}")
    print(f"[質問] {args.question}\n")
    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
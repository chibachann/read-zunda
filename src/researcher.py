"""
researcher.py - Research Module

Claude APIのweb_searchツールを使って指定テーマのリサーチを行うモジュール。
設計書: DESIGN.md § 3.1 Research Module
"""

import anthropic


def fetch_research(theme: str, client: anthropic.Anthropic) -> str:
    """
    指定したテーマについてClaude APIでWebリサーチを行う。

    Args:
        theme: リサーチするテーマ文字列（例: "量子コンピュータの最新動向"）
        client: Anthropic APIクライアント

    Returns:
        リサーチ結果のテキスト（複数ソースの情報をまとめたもの）
    """
    prompt = (
        f"「{theme}」について詳しくリサーチしてください。"
        "最新の情報を複数のソースから収集し、重要なポイントをすべて含めた"
        "詳細なリサーチ結果を日本語でまとめてください。"
    )

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    # テキストブロックのみ結合して返す
    result_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            result_parts.append(block.text)

    return "\n".join(result_parts)

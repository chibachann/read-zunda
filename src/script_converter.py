"""
script_converter.py - Script Converter

Markdownテキストを音声読み上げ向けのプレーンテキストに変換するモジュール。
設計書: DESIGN.md § 3.3 Script Converter
"""

import re


def convert_to_script(markdown_text: str) -> str:
    """
    Markdownテキストを音声読み上げ用のプレーンテキストに変換する。

    変換ルール:
    - 見出し（#）→ 自然な読み上げ文に変換
    - コードブロック → 「コードは省略します」に置換
    - URLリンク → リンクテキストのみ残す
    - 箇条書き → 読点で繋いだ文章に変換
    - 水平線（---）→ 改行に変換

    Args:
        markdown_text: 変換元のMarkdownテキスト

    Returns:
        音声読み上げ向けのプレーンテキスト
    """
    text = markdown_text

    # コードブロックを除去
    text = re.sub(r"```[\s\S]*?```", "コードは省略します。", text)

    # インラインコードを除去
    text = re.sub(r"`[^`]+`", "", text)

    # 見出しを自然な文章に変換（# → 。改行、## → 。改行）
    text = re.sub(r"^#{1,6}\s+(.+)$", r"\1。", text, flags=re.MULTILINE)

    # URLリンク [テキスト](URL) → テキスト
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # 画像 ![alt](URL) → 除去
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)

    # 箇条書き行を収集して読点で繋ぐ
    text = _convert_list_items(text)

    # 太字・斜体を除去
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)

    # 水平線を除去
    text = re.sub(r"^[-*_]{3,}$", "", text, flags=re.MULTILINE)

    # 表（テーブル）を除去
    text = re.sub(r"^\|.*\|$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s|:-]+$", "", text, flags=re.MULTILINE)

    # 3行以上の連続空行を2行に圧縮
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _convert_list_items(text: str) -> str:
    """
    連続する箇条書き行をまとめて読点区切りの文章に変換する。

    Args:
        text: 変換元テキスト

    Returns:
        箇条書きを文章に変換したテキスト
    """
    lines = text.split("\n")
    result = []
    list_buffer = []

    for line in lines:
        # 箇条書き行（- または * または 数字. で始まる行）
        match = re.match(r"^[\s]*[-*]\s+(.+)$", line) or re.match(
            r"^[\s]*\d+\.\s+(.+)$", line
        )
        if match:
            list_buffer.append(match.group(1))
        else:
            # 箇条書きが終わったらまとめて出力
            if list_buffer:
                result.append("、".join(list_buffer) + "。")
                list_buffer = []
            result.append(line)

    # 末尾に箇条書きが残っていた場合
    if list_buffer:
        result.append("、".join(list_buffer) + "。")

    return "\n".join(result)

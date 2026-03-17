"""
doc_generator.py - Document Generator

リサーチ結果をMarkdownドキュメントに整形して保存するモジュール。
設計書: DESIGN.md § 3.2 Document Generator
"""

import anthropic
from datetime import datetime
from pathlib import Path


def generate_document(
    theme: str,
    research_text: str,
    client: anthropic.Anthropic,
    output_dir: Path,
) -> tuple[str, Path]:
    """
    リサーチ結果をMarkdownドキュメントに整形し、ファイルに保存する。

    Args:
        theme: リサーチしたテーマ文字列
        research_text: researcher.pyが返したリサーチ結果テキスト
        client: Anthropic APIクライアント
        output_dir: ドキュメントの保存先ディレクトリ

    Returns:
        tuple: (Markdownテキスト, 保存したファイルのPath)
    """
    prompt = f"""以下のリサーチ結果を、読みやすいMarkdownドキュメントに整形してください。

必ず以下の構成で出力してください（日本語）:

# （テーマに合ったタイトル）

## 概要
（3〜5文でテーマの概要を説明）

## 主要ポイント
- ポイント1
- ポイント2
- ...

## 詳細
（詳しい内容を複数のサブセクションに分けて記述）

## まとめ
（重要な結論・考察を3〜5文で）

---
テーマ: {theme}

リサーチ結果:
{research_text}
"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    markdown_text = response.content[0].text

    # ファイル保存（YYYYMMDD_テーマ.md）
    date_str = datetime.now().strftime("%Y%m%d")
    safe_theme = theme.replace(" ", "_").replace("/", "_")[:30]
    filename = f"{date_str}_{safe_theme}.md"
    output_path = output_dir / filename

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_text, encoding="utf-8")

    return markdown_text, output_path

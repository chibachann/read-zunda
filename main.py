"""
main.py - エントリーポイント

read-zunda の CLI インターフェース。
テーマを受け取り、リサーチ → ドキュメント生成 → 読み上げを一括実行する。

使い方:
    python main.py --theme "調べたいテーマ"

設計書: DESIGN.md § 5 インターフェース設計
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from src.researcher import fetch_research
from src.doc_generator import generate_document
from src.script_converter import convert_to_script
from src.voicevox_client import synthesize_voice, check_voicevox_running
from src.audio_player import play_audio


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数を解析する。

    Returns:
        解析済みの引数オブジェクト
    """
    parser = argparse.ArgumentParser(
        description="Claude Codeがリサーチした内容をずんだもんが読み上げるソフト"
    )
    parser.add_argument(
        "--theme",
        required=True,
        help="リサーチするテーマ（例: '量子コンピュータの最新動向'）",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="出力先ディレクトリ（デフォルト: ./output）",
    )
    parser.add_argument(
        "--save-audio",
        action="store_true",
        help="音声ファイルを保存する（デフォルト: 保存しない）",
    )
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="読み上げをスキップする",
    )
    return parser.parse_args()


def main() -> None:
    """
    メイン処理。

    1. リサーチ
    2. ドキュメント生成
    3. 読み上げスクリプト変換
    4. 音声合成
    5. 音声再生
    """
    load_dotenv()

    args = parse_args()
    output_dir = Path(args.output_dir)
    docs_dir = output_dir / "docs"
    audio_dir = output_dir / "audio"

    # Anthropic クライアント初期化
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: ANTHROPIC_API_KEY が設定されていません。.envファイルを確認してください。")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # VOICEVOX 起動確認（--no-play でない場合のみ）
    voicevox_host = os.getenv("VOICEVOX_HOST", "http://localhost:50021")
    if not args.no_play:
        if not check_voicevox_running(voicevox_host):
            print(
                f"エラー: VOICEVOX が起動していません。{voicevox_host} を確認してください。"
            )
            sys.exit(1)

    # Step 1: リサーチ
    print(f"\n🔍 リサーチ中: 「{args.theme}」")
    research_text = fetch_research(args.theme, client)
    print("✅ リサーチ完了")

    # Step 2: ドキュメント生成
    print("\n📝 ドキュメント生成中...")
    markdown_text, doc_path = generate_document(
        args.theme, research_text, client, docs_dir
    )
    print(f"✅ ドキュメント保存: {doc_path}")

    # Step 3: 読み上げスクリプト変換
    print("\n🔄 読み上げスクリプト変換中...")
    script = convert_to_script(markdown_text)
    print("✅ 変換完了")

    # Step 4 & 5: 音声合成 → 再生
    if not args.no_play:
        print("\n🎙️ 音声合成中（ずんだもん）...")
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_theme = args.theme.replace(" ", "_")[:30]
        wav_filename = f"{date_str}_{safe_theme}.wav"

        # --save-audio が指定された場合はファイル保存、そうでなければ一時ファイル
        if args.save_audio:
            wav_path = audio_dir / wav_filename
        else:
            wav_path = Path("/tmp") / wav_filename

        wav_path = synthesize_voice(script, wav_path, host=voicevox_host)
        print(f"✅ 音声合成完了: {wav_path}")

        print("\n🔊 再生中...")
        play_audio(wav_path)
        print("✅ 再生完了")

        # 一時ファイルを削除（--save-audio でない場合）
        if not args.save_audio and wav_path.exists():
            wav_path.unlink()
    else:
        print("\n⏭️  読み上げをスキップしました")

    print(f"\n✨ 完了！ドキュメント: {doc_path}")


if __name__ == "__main__":
    main()

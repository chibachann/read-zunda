"""
audio_player.py - Audio Player

WAVファイルを再生するモジュール。
設計書: DESIGN.md § 3.5 Audio Player
"""

import subprocess
import sys
from pathlib import Path


def play_audio(wav_path: Path) -> None:
    """
    WAVファイルを再生する。

    macOS では afplay コマンドを使用する。
    afplay はmacOS標準コマンドのため追加インストール不要。

    Args:
        wav_path: 再生するWAVファイルのパス

    Raises:
        FileNotFoundError: 指定したWAVファイルが存在しない場合
        RuntimeError: 再生に失敗した場合
    """
    if not wav_path.exists():
        raise FileNotFoundError(f"WAVファイルが見つかりません: {wav_path}")

    if sys.platform == "darwin":
        # macOS: afplay コマンドで再生
        result = subprocess.run(
            ["afplay", str(wav_path)],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"音声再生に失敗しました: {result.stderr.decode()}")
    else:
        # Linux / Windows: aplay / powershell など（拡張候補）
        raise NotImplementedError(
            f"このプラットフォームはまだ対応していません: {sys.platform}"
        )

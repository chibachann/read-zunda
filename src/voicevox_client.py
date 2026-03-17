"""
voicevox_client.py - VOICEVOX Client

VOICEVOX HTTP APIを使って音声合成を行うモジュール。
設計書: DESIGN.md § 3.4 VOICEVOX Client
"""

import requests
from pathlib import Path


# ずんだもんの話者ID（VOICEVOX デフォルト）
ZUNDAMON_SPEAKER_ID = 3


def synthesize_voice(
    text: str,
    output_path: Path,
    host: str = "http://localhost:50021",
    speaker_id: int = ZUNDAMON_SPEAKER_ID,
) -> Path:
    """
    テキストをVOICEVOXで音声合成してWAVファイルに保存する。

    VOICEVOXのAPIフロー:
    1. POST /audio_query  → 音声クエリ（発音・アクセント情報）を生成
    2. POST /synthesis    → クエリを元に音声合成してWAVバイナリを取得

    Args:
        text: 読み上げるテキスト
        output_path: WAVファイルの保存先パス
        host: VOICEVOXのホストURL（デフォルト: http://localhost:50021）
        speaker_id: 話者ID（デフォルト: 3 = ずんだもん）

    Returns:
        保存したWAVファイルのPath

    Raises:
        requests.HTTPError: VOICEVOX APIがエラーを返した場合
        requests.ConnectionError: VOICEVOXが起動していない場合
    """
    # Step 1: 音声クエリの生成
    query_response = requests.post(
        f"{host}/audio_query",
        params={"text": text, "speaker": speaker_id},
    )
    query_response.raise_for_status()
    audio_query = query_response.json()

    # Step 2: 音声合成
    synthesis_response = requests.post(
        f"{host}/synthesis",
        params={"speaker": speaker_id},
        json=audio_query,
    )
    synthesis_response.raise_for_status()

    # WAVファイルに保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(synthesis_response.content)

    return output_path


def check_voicevox_running(host: str = "http://localhost:50021") -> bool:
    """
    VOICEVOXが起動しているか確認する。

    Args:
        host: VOICEVOXのホストURL

    Returns:
        起動していればTrue、そうでなければFalse
    """
    try:
        response = requests.get(f"{host}/version", timeout=3)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

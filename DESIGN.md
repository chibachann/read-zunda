# read-zunda 設計書

## 1. システム概要

指定したテーマについてClaude Codeがリサーチを行い、内容をドキュメントにまとめ、VOICEVOXのずんだもんボイスで読み上げるシステム。

---

## 2. システム構成図

```
ユーザー
  │
  │ テーマ入力
  ▼
┌─────────────────────┐
│      CLI / UI       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Research Module   │ ← Claude API（Web検索・情報収集）
└──────────┬──────────┘
           │ リサーチ結果（raw text）
           ▼
┌─────────────────────┐
│  Document Generator │ ← Claude API（要約・整形）
└──────────┬──────────┘
           │ Markdownドキュメント
           ▼
┌─────────────────────┐
│   Script Converter  │ ← 読み上げ用テキストに変換
└──────────┬──────────┘
           │ 読み上げスクリプト
           ▼
┌─────────────────────┐
│   VOICEVOX Client   │ ← VOICEVOX HTTP API
└──────────┬──────────┘
           │ 音声ファイル（WAV）
           ▼
┌─────────────────────┐
│   Audio Player      │ ← 再生 or ファイル保存
└─────────────────────┘
```

---

## 3. モジュール設計

### 3.1 Research Module

| 項目 | 内容 |
|------|------|
| 役割 | 指定テーマについてWebリサーチを行い、生の情報を収集する |
| 入力 | テーマ文字列（例: "量子コンピュータの最新動向"） |
| 出力 | リサーチ結果テキスト（複数ソースの情報をまとめたもの） |
| 使用技術 | Claude API（`web_search` ツール） |

### 3.2 Document Generator

| 項目 | 内容 |
|------|------|
| 役割 | リサーチ結果を読みやすいMarkdownドキュメントに整形する |
| 入力 | リサーチ結果テキスト |
| 出力 | Markdownファイル（`output/YYYYMMDD_テーマ.md`） |
| 使用技術 | Claude API |

**出力ドキュメント構成:**
```
# タイトル
## 概要（3〜5文）
## 主要ポイント
- ポイント1
- ポイント2
## 詳細
...
## まとめ
```

### 3.3 Script Converter

| 項目 | 内容 |
|------|------|
| 役割 | Markdownを音声読み上げ向けのプレーンテキストに変換する |
| 入力 | Markdownテキスト |
| 出力 | 読み上げ用スクリプト（見出し記号・コードブロック等を除去） |
| 使用技術 | Python（正規表現による変換） |

**変換ルール:**
- `#` 見出し → 「〇〇について」などの自然な読み上げ文に変換
- コードブロック → スキップ or 「コードは省略します」
- URLリンク → リンクテキストのみ残す
- 箇条書き → 読点で繋いだ文章に変換

### 3.4 VOICEVOX Client

| 項目 | 内容 |
|------|------|
| 役割 | VOICEVOX APIを叩いて音声合成を行う |
| 入力 | 読み上げテキスト、話者ID（ずんだもん: 3） |
| 出力 | WAVファイル |
| 使用技術 | VOICEVOX HTTP API、Python `requests` |

**VOICEVOX APIフロー:**
```
POST /audio_query  → クエリ生成
POST /synthesis    → 音声合成
→ WAVバイナリ取得
```

### 3.5 Audio Player

| 項目 | 内容 |
|------|------|
| 役割 | 生成した音声を再生する |
| 入力 | WAVファイル |
| 出力 | 音声再生 または ファイル保存 |
| 使用技術 | Python `pygame` or `simpleaudio` |

---

## 4. ディレクトリ構成

```
read-zunda/
├── README.md
├── DESIGN.md
├── requirements.txt
├── main.py                  # エントリーポイント
├── src/
│   ├── researcher.py        # Research Module
│   ├── doc_generator.py     # Document Generator
│   ├── script_converter.py  # Script Converter
│   ├── voicevox_client.py   # VOICEVOX Client
│   └── audio_player.py      # Audio Player
├── output/
│   ├── docs/                # 生成されたMarkdownドキュメント
│   └── audio/               # 生成されたWAVファイル
└── tests/
    └── ...
```

---

## 5. インターフェース設計

### CLIコマンド

```bash
# 基本的な使い方
python main.py --theme "調べたいテーマ"

# オプション
python main.py --theme "テーマ" \
  --save-doc        # ドキュメントをファイル保存（デフォルト: 保存する）
  --save-audio      # 音声をファイル保存（デフォルト: 保存しない）
  --no-play         # 読み上げをスキップ
  --output-dir ./output  # 出力先ディレクトリ
```

---

## 6. 外部依存

| 依存 | 用途 | 備考 |
|------|------|------|
| `anthropic` | Claude API | リサーチ・ドキュメント生成 |
| `requests` | HTTP通信 | VOICEVOX API呼び出し |
| `pygame` | 音声再生 | WAV再生 |
| `python-dotenv` | 環境変数管理 | APIキー管理 |

### 環境変数

```
ANTHROPIC_API_KEY=your_api_key
VOICEVOX_HOST=http://localhost:50021  # VOICEVOXのデフォルトポート
```

---

## 7. 前提条件

- Python 3.11+
- VOICEVOX がローカルで起動していること（`http://localhost:50021`）
- Anthropic APIキーが取得済みであること

---

## 8. 今後の拡張候補

- [ ] GUIの追加（tkinter or Streamlit）
- [ ] 複数話者の選択対応
- [ ] 読み上げ速度・ピッチの調整
- [ ] 定期的な自動リサーチ（スケジューラ連携）
- [ ] ポッドキャスト形式への出力（複数テーマを連結）

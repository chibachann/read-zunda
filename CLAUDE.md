# read-zunda 開発ルール

## 設計書

実装前に必ず以下の設計書を読むこと。

- **設計書**: `/Users/chiba/Develop/read-zunda/DESIGN.md`

---

## ブランチ運用

- `main` ブランチへの直接コミットは禁止
- 機能追加・修正は必ずブランチを切って開発する
- ブランチ命名規則: `feature/機能名`（例: `feature/research-module`）
- **マージは人間が最終確認・承認してから行う**
- Claude はブランチへのコミット・プッシュまでを担当し、マージは人間が指示した場合のみ実行する

```bash
# ブランチ作成
git checkout -b feature/機能名

# 実装完了後：コミット＆プッシュまで行い、マージは人間に確認する
git push origin feature/機能名
```

---

## コメント規則

- 関数・クラスには必ずdocstringを記載する
- 処理の意図が分かりにくい箇所にはインラインコメントを入れる
- コメントは日本語で記載する

```python
def fetch_research(theme: str) -> str:
    """
    指定したテーマについてClaude APIでリサーチを行う。

    Args:
        theme: リサーチするテーマ文字列

    Returns:
        リサーチ結果のテキスト
    """
```

---

## その他

- Python 3.11+ を使用する
- 環境変数は `.env` で管理し、`.env` はコミットしない

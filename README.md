# ✍️ AI ライティングツール

Gemini API を使った、個人用のライティング支援ツール。
ブログ執筆・メール返信・要約などの機能を 1 つの Streamlit アプリにまとめています。
データベースやログイン機能はありません（ローカルで自分だけで使う前提）。

## 搭載機能

| 機能 | 説明 |
|------|------|
| 📝 ブログ記事の執筆 | テーマ・読者・文体・分量を指定して記事を丸ごと生成 |
| ✉️ メール返信文の作成 | 受信メールと返信意図から返信の下書きを作成 |
| 📄 文章の要約 | 3行 / 箇条書き / 段落 / エグゼクティブサマリー形式で要約 |
| 🔍 校正・推敲 | 誤字脱字・不自然な表現を修正し、修正点の一覧も出力 |
| 🎚️ トーン変換・言い換え | 丁寧 / カジュアル / 簡潔 / 英訳など、同じ内容を書き換え |
| 📣 SNS 投稿文の作成 | X・LinkedIn・Instagram 等に合わせた投稿文を複数案生成 |
| 💡 タイトル案・構成案 | タイトル候補 10 個、見出し構成、詳細アウトライン |

## セットアップ

### 1. API キーを取得

[Google AI Studio](https://aistudio.google.com/apikey) で API キーを発行します（無料枠あり）。

### 2. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

（仮想環境を使う場合は先に `python -m venv .venv` してから有効化）

### 3. API キーを設定

いずれかの方法で：

- **`.env` ファイル（おすすめ）**: `.env.example` を `.env` にコピーして `GEMINI_API_KEY` を記入
- **環境変数**: `GEMINI_API_KEY` または `GOOGLE_API_KEY` を設定
- **アプリのサイドバー**: 起動後に直接入力（そのセッションのみ有効）

## 起動

```bash
python -m streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

> `streamlit run app.py` でも起動できますが、`streamlit` コマンドが「見つかりません」に
> なる場合はインストール先の `Scripts` フォルダが PATH に入っていません。
> 上記のように `python -m streamlit ...` と書けば PATH 設定なしで動きます。

## 使い方

1. 上部のボタンで機能を選ぶ
2. フォームに入力（`*` が必須項目）
3. 「✨ 生成する」を押す
4. 結果はストリーミング表示され、下部でテキスト保存・コピーができる
5. 同じセッション中の生成結果は「履歴」に最大 20 件残る

サイドバーの「生成パラメータ」で `Temperature`（創造性）と最大出力トークンを調整できます。
モデルはサイドバーで切り替え可能です（デフォルトは最新の安定版 Flash）。

## プロジェクト構成

```
python-ai-application/
├── app.py               … Streamlit の画面（入力フォーム・結果表示・履歴）
├── config.py            … モデル一覧・既定パラメータ
├── ai_core/
│   ├── client.py        … Gemini API 呼び出し（generate / generate_stream）
│   └── registry.py      … 機能を登録・取得する仕組み（Feature / Field）
└── features/            … 機能 1 つ = 1 ファイル
    ├── __init__.py      … 全機能を import して登録（表示順もここ）
    ├── blog_writer.py
    ├── email_reply.py
    ├── summarizer.py
    ├── proofreader.py
    ├── tone_converter.py
    ├── sns_post.py
    └── title_ideas.py
```

## 新しい機能を追加する

`features/` にファイルを 1 つ作り、`Feature` を組み立てて `register()` に渡すだけです。

```python
# features/my_feature.py
from typing import Any
from ai_core import Feature, Field, register

def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    # (system_instruction, user_prompt) を返す
    return "あなたは...", f"次の内容を...: {inputs['text']}"

register(Feature(
    key="my_feature",
    label="私の機能",
    icon="🚀",
    description="何をする機能かの一言説明",
    temperature=0.7,
    fields=(
        Field("text", "入力テキスト", kind="textarea", required=True),
    ),
    build_prompt=_build,
))
```

最後に `features/__init__.py` の import に `my_feature` を 1 行足せば、メニューに出てきます。

`Field` の `kind` は `text` / `textarea` / `select` / `slider` に対応しています。

## 注意

- API キーは `.env` に入れて、`.gitignore` 済みなのでコミットしないでください。
- Gemini API の無料枠にはレート制限があります。大量に使う場合は課金設定を確認してください。
- モデル名は時期によって変わります。エラーが出たらサイドバーで別のモデルを選ぶか、`config.py` の `AVAILABLE_MODELS` を更新してください。
- 入力内容は Google Gemini API に送信されます。機微情報を扱う場合は各自の規程を確認してください。

## セキュリティ

このアプリは **ローカルで自分だけが使う** 前提で作られています（`.streamlit/config.toml`
で `localhost` のみ待ち受け）。セキュリティレビューの詳細は `SECURITY_REVIEW.md` を参照。

**社内・インターネットに公開する場合は、公開前に必ず以下を行ってください:**

- **認証を追加する** — 認証がないまま公開すると、URL を知る全員があなたの API キーの
  費用を消費できます。Streamlit ネイティブ認証（`st.login` + OIDC）か、前段のリバース
  プロキシ / SSO を設置してください。
- **共有 API キーは環境変数に置く** — サイドバーの入力欄ではなく `GEMINI_API_KEY` を
  サーバー側に設定し、UI 入力を無効化します（`resolve_api_key` が環境変数を優先します）。
- **`config.py` の生成上限を見直す** — `MAX_OUTPUT_TOKENS_LIMIT` / `RATE_LIMIT_MAX` /
  `MAX_INPUT_CHARS` を運用に合わせて調整。Google Cloud 側でキーに予算上限を設定。
- **依存を監査する** — `pip install -r requirements.txt` 後に `pip-audit` を実行。
- **HTTPS で配信する** — 前段で TLS 終端し、平文 HTTP で公開しない。

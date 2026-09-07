"""アプリ全体の設定値。"""

from __future__ import annotations

# 利用可能なモデル。先頭がデフォルト。
# 新しいモデルが出たらここに文字列を足すだけで UI の選択肢に反映される。
#   *-latest エイリアスは Google 側で常に最新の安定版を指すので、
#   基本はこれを使えばモデル更新に追従できる。
AVAILABLE_MODELS: list[str] = [
    "gemini-flash-latest",       # 最新の安定版 Flash（推奨・自動追従）
    "gemini-3.8-flash",          # 2026-09 時点の最新 Flash（明示ピン）
    "gemini-3.7-flash",
    "gemini-pro-latest",         # 最新の安定版 Pro（高難度向け・低速/高コスト）
    "gemini-3.1-pro-preview",
    "gemini-flash-lite-latest",  # 最速・最安（下書き・大量処理向け）
]

DEFAULT_MODEL: str = AVAILABLE_MODELS[0]

# 環境変数からキーを読む場合の候補名（上から順に探す）。
API_KEY_ENV_VARS: tuple[str, ...] = ("GEMINI_API_KEY", "GOOGLE_API_KEY")

APP_TITLE = "AI ライティングツール"
APP_ICON = "✍️"

# 生成のデフォルトパラメータ。
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 8192

# 生成コストの上限。
#   MAX_OUTPUT_TOKENS_LIMIT … サイドバーのスライダー上限。青天井にすると
#     （特に公開時に）1 リクエストで課金枠を大量消費できてしまうため絞る。
#   MAX_INPUT_CHARS          … 1 入力欄あたりの文字数上限。
#   RATE_LIMIT_MAX / _WINDOW_SEC … 1 セッションあたり WINDOW 秒で MAX 回まで生成可。
MAX_OUTPUT_TOKENS_LIMIT = 8192
MAX_INPUT_CHARS = 20000
RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW_SEC = 60

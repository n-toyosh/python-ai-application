"""AI ライティングツール — Streamlit エントリポイント.

起動:  streamlit run app.py
"""

from __future__ import annotations

import datetime as _dt
import re
import time
from typing import Any

import streamlit as st
from dotenv import load_dotenv

import config
import features  # noqa: F401  (import することで全機能がレジストリに登録される)
from ai_core import GeminiError, all_features, generate_stream, resolve_api_key

load_dotenv()

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout="wide")


# --------------------------------------------------------------------------- #
# セッション状態
# --------------------------------------------------------------------------- #
def _init_state() -> None:
    st.session_state.setdefault("history", [])          # list[dict]
    st.session_state.setdefault("api_key_input", "")
    st.session_state.setdefault("last_output", None)    # dict | None
    st.session_state.setdefault("gen_times", [])        # list[float]  レート制限用の生成時刻


# --------------------------------------------------------------------------- #
# モデル出力のサニタイズ
# --------------------------------------------------------------------------- #
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)\s]*\)")


def _sanitize_model_markdown(text: str) -> str:
    """モデル出力を Markdown として描画する前に画像記法を無害化する。

    要約・メール返信などの機能では「他人が書いた文章」をそのまま入力するため、
    その文章に仕込まれた指示でモデルが `![](http://攻撃者/…)` のような画像記法を
    出力すると、結果や履歴を表示した瞬間にブラウザが攻撃者へリクエストを送る
    （閲覧ビーコン／少量のデータ送出）。画像はテキスト表現に置き換える。
    """
    if not text:
        return text
    return _MD_IMAGE_RE.sub(
        lambda m: f"［画像: {m.group(1)}］" if m.group(1) else "［画像］", text
    )


def _check_rate_limit() -> bool:
    """直近 RATE_LIMIT_WINDOW_SEC 秒の生成回数が上限内なら True。"""
    now = time.monotonic()
    window = config.RATE_LIMIT_WINDOW_SEC
    recent = [t for t in st.session_state["gen_times"] if now - t < window]
    st.session_state["gen_times"] = recent
    return len(recent) < config.RATE_LIMIT_MAX


_init_state()


# --------------------------------------------------------------------------- #
# サイドバー
# --------------------------------------------------------------------------- #
def _render_sidebar(default_temperature: float) -> dict[str, Any]:
    with st.sidebar:
        st.header("⚙️ 設定")

        env_key = resolve_api_key(None)
        if env_key:
            st.success("API キーを環境変数 / .env から読み込みました。", icon="✅")
            api_key = env_key
        else:
            api_key = st.text_input(
                "Gemini API キー",
                type="password",
                value=st.session_state["api_key_input"],
                help="https://aistudio.google.com/apikey で取得。"
                "\n\n毎回入力したくない場合は .env に GEMINI_API_KEY を書いてください。",
            )
            st.session_state["api_key_input"] = api_key

        model = st.selectbox("モデル", config.AVAILABLE_MODELS, index=0)

        with st.expander("生成パラメータ"):
            temperature = st.slider(
                "Temperature（創造性）", 0.0, 1.5, default_temperature, 0.1,
                key=f"temp_{default_temperature}",
                help="低いほど堅実で一貫、高いほど多様で創造的。"
                "機能ごとの推奨値を初期表示しています。",
            )
            max_tokens = st.slider(
                "最大出力トークン",
                512,
                config.MAX_OUTPUT_TOKENS_LIMIT,
                min(config.DEFAULT_MAX_OUTPUT_TOKENS, config.MAX_OUTPUT_TOKENS_LIMIT),
                512,
            )

        st.divider()
        st.caption(f"{config.APP_ICON} {config.APP_TITLE}")
        st.caption(
            "⚠️ 入力内容は Google Gemini API に送信されます。"
            "機微情報の取り扱いは各自の規程に従ってください。"
        )

    return {
        "api_key": api_key,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


# --------------------------------------------------------------------------- #
# 入力フォーム
# --------------------------------------------------------------------------- #
def _render_field(field, ns: str) -> Any:
    # feature ごとにウィジェットキーを分ける。
    # （同名フィールドが別 feature にあっても値やオプションが混ざらないように）
    key = f"field_{ns}_{field.key}"
    label = field.label + ("  *" if field.required else "")
    if field.kind == "textarea":
        return st.text_area(
            label, key=key, height=field.height,
            placeholder=field.placeholder, help=field.help,
            max_chars=config.MAX_INPUT_CHARS,
        )
    if field.kind == "select":
        options = list(field.options)
        index = options.index(field.default) if field.default in options else 0
        return st.selectbox(label, options, index=index, key=key, help=field.help)
    if field.kind == "slider":
        # min/max/step/value は Streamlit 上で型を揃える必要がある。
        # すべて整数なら int スライダー、それ以外は float スライダーにする。
        is_int = all(
            float(v).is_integer() for v in (field.min, field.max, field.step)
        )
        cast = int if is_int else float
        default = field.default if field.default is not None else field.min
        return st.slider(
            label,
            cast(field.min), cast(field.max), cast(default), cast(field.step),
            key=key, help=field.help,
        )
    return st.text_input(
        label, key=key, placeholder=field.placeholder, help=field.help,
        max_chars=config.MAX_INPUT_CHARS,
    )


def _collect_inputs(feature) -> tuple[dict[str, Any], list[str]]:
    values: dict[str, Any] = {}
    missing: list[str] = []
    for field in feature.fields:
        value = _render_field(field, feature.key)
        values[field.key] = value
        if field.required and (value is None or str(value).strip() == ""):
            missing.append(field.label)
    return values, missing


# --------------------------------------------------------------------------- #
# メイン
# --------------------------------------------------------------------------- #
def main() -> None:
    feats = all_features()

    st.title(f"{config.APP_ICON} {config.APP_TITLE}")

    labels = [f.menu_label for f in feats]
    chosen_label = st.radio(
        "機能を選択", labels, horizontal=True, label_visibility="collapsed",
    )
    feature = feats[labels.index(chosen_label)]

    settings = _render_sidebar(feature.temperature)

    st.subheader(f"{feature.icon}  {feature.label}")
    st.caption(feature.description)

    with st.form(key=f"form_{feature.key}"):
        inputs, missing = _collect_inputs(feature)
        submitted = st.form_submit_button("✨ 生成する", type="primary", use_container_width=True)

    if submitted:
        _handle_submit(feature, inputs, missing, settings)

    _render_last_output()
    _render_history()


def _handle_submit(feature, inputs, missing, settings) -> None:
    if not settings["api_key"]:
        st.error("サイドバーで Gemini API キーを入力してください。")
        return
    if missing:
        st.warning("必須項目が未入力です: " + " / ".join(missing))
        return
    if not _check_rate_limit():
        st.warning(
            f"短時間に生成しすぎです（{config.RATE_LIMIT_WINDOW_SEC} 秒あたり "
            f"{config.RATE_LIMIT_MAX} 回まで）。少し待ってから再試行してください。"
        )
        return

    system_instruction, prompt = feature.build_prompt(inputs)
    st.session_state["gen_times"].append(time.monotonic())

    st.markdown("### 生成結果")
    placeholder = st.empty()
    chunks: list[str] = []
    try:
        with st.spinner("生成中…"):
            stream = generate_stream(
                prompt,
                api_key=settings["api_key"],
                model=settings["model"],
                system_instruction=system_instruction,
                temperature=settings["temperature"],
                max_output_tokens=settings["max_tokens"],
            )
            for piece in stream:
                chunks.append(piece)
                # モデル出力はそのまま Markdown 描画せず、都度サニタイズする。
                placeholder.markdown(_sanitize_model_markdown("".join(chunks)))
    except GeminiError as exc:
        st.error(str(exc))
        return

    text = "".join(chunks)
    if not text or not text.strip():
        st.error("モデルから空の応答が返りました。設定やプロンプトを変えて再試行してください。")
        return

    entry = {
        "feature": feature.label,
        "icon": feature.icon,
        "model": settings["model"],
        "time": _dt.datetime.now().strftime("%H:%M:%S"),
        "output": text,
    }
    st.session_state["last_output"] = entry
    st.session_state["history"].insert(0, entry)
    del st.session_state["history"][20:]


def _render_last_output() -> None:
    entry = st.session_state.get("last_output")
    if not entry:
        return
    st.download_button(
        "⬇️ テキストで保存",
        data=entry["output"],
        file_name=f"{entry['feature']}_{_dt.date.today()}.md",
        mime="text/markdown",
    )
    with st.expander("最新の結果（コピー用プレーンテキスト）"):
        st.code(entry["output"], language="markdown")


def _render_history() -> None:
    history = st.session_state.get("history", [])
    if not history:
        return
    st.divider()
    st.subheader("🕘 このセッションの履歴")
    for entry in history:
        title = f"{entry['icon']} {entry['feature']}  —  {entry['time']}  ({entry['model']})"
        with st.expander(title):
            st.markdown(_sanitize_model_markdown(entry["output"]))
    if st.button("履歴をクリア"):
        st.session_state["history"] = []
        st.session_state["last_output"] = None
        st.rerun()


if __name__ == "__main__":
    main()

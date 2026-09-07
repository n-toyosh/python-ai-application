"""タイトル案・見出し案・アウトラインを出す。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは編集者兼コピーライターです。読み手のベネフィットが伝わり、"
    "煽りすぎない魅力的なタイトルや構成案を提案します。"
)

_MODES = {
    "タイトル案を10個": (
        "本文の内容に合うタイトルを10個提案してください。"
        "それぞれ狙い（例: 数字訴求 / 問いかけ / How-to）を一言添えてください。"
    ),
    "見出し（H2/H3）構成案": (
        "記事の見出し構成案を Markdown の階層（##, ###）で作ってください。"
        "各見出しに1行で「何を書くか」のメモを添えてください。"
    ),
    "アウトライン（詳細）": (
        "導入・本論・結論の詳細アウトラインを作ってください。"
        "各セクションに要点を箇条書きで3個程度。"
    ),
}


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    mode = inputs.get("mode", next(iter(_MODES)))
    theme = inputs["theme"].strip()
    body = inputs.get("body", "").strip()
    audience = inputs.get("audience", "").strip()

    lines = [_MODES.get(mode, "")]
    lines.append(f"テーマ: {theme}")
    if audience:
        lines.append(f"想定読者: {audience}")
    if body:
        lines += ["", "--- 本文または下書き（参考）---", body]
    return _SYSTEM, "\n".join(line for line in lines if line)


register(
    Feature(
        key="ideas",
        label="タイトル案・構成案",
        icon="💡",
        description="ブログや資料のタイトル候補、見出し構成、アウトラインを出します。",
        temperature=0.9,
        fields=(
            Field(
                "mode",
                "ほしいもの",
                kind="select",
                options=tuple(_MODES.keys()),
            ),
            Field(
                "theme",
                "テーマ・仮タイトル",
                kind="textarea",
                required=True,
                height=90,
            ),
            Field("audience", "想定読者（任意）"),
            Field(
                "body",
                "本文・下書き（任意・あると精度が上がる）",
                kind="textarea",
                height=180,
            ),
        ),
        build_prompt=_build,
    )
)

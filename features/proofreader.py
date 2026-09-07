"""文章の校正・推敲を行う。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは日本語の校正者です。誤字脱字・変換ミス・文法の誤り・不自然な表現・"
    "冗長さ・表記ゆれを指摘し、より自然で読みやすい文章に直します。"
    "書き手の意図やニュアンスは変えません。"
)

_LEVELS = {
    "軽め（誤字・文法のみ）": "明らかな誤字脱字・文法・変換ミスだけを直してください。表現の好みには踏み込まないこと。",
    "標準（読みやすさも改善）": "誤りに加えて、冗長な部分や不自然な言い回しも自然に整えてください。",
    "がっつり（構成から推敲）": "誤りの修正に加え、段落構成や論理の流れも見直し、必要なら大きく書き換えてください。",
}


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    text = inputs["text"].strip()
    level = inputs.get("level", "標準（読みやすさも改善）")
    style = inputs.get("style", "原文に合わせる")

    lines = [
        _LEVELS.get(level, _LEVELS["標準（読みやすさも改善）"]),
        f"文体は「{style}」で統一してください。",
        "",
        "次の2部構成で出力してください。",
        "## 修正後の文章",
        "（推敲済みの全文）",
        "",
        "## 主な修正点",
        "（何をなぜ直したかを箇条書きで。重要なものだけ、最大8個）",
        "",
        "--- 元の文章 ---",
        text,
    ]
    return _SYSTEM, "\n".join(lines)


register(
    Feature(
        key="proofread",
        label="校正・推敲",
        icon="🔍",
        description="誤字脱字や不自然な表現を直し、修正点の一覧も返します。",
        temperature=0.3,
        fields=(
            Field(
                "text",
                "チェックしたい文章",
                kind="textarea",
                required=True,
                height=280,
            ),
            Field(
                "level",
                "直しの強さ",
                kind="select",
                options=tuple(_LEVELS.keys()),
            ),
            Field(
                "style",
                "整える文体",
                kind="select",
                options=("原文に合わせる", "です・ます調", "だ・である調"),
            ),
        ),
        build_prompt=_build,
    )
)

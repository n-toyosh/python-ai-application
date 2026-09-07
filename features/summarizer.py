"""文章を要約する。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは正確な要約を作る編集者です。原文にない情報を足さず、"
    "重要な論点・数値・結論を落とさずにまとめます。"
)

_FORMAT_INSTRUCTIONS = {
    "3行まとめ": "全体を3行（各行1文）で要約してください。",
    "箇条書き（5点以内）": "最大5個の箇条書きで要点をまとめてください。",
    "段落（200字程度）": "200字程度の1〜2段落で要約してください。",
    "エグゼクティブサマリー": (
        "冒頭に結論を1文、続けて背景・要点・示唆を各1〜2文でまとめた"
        "エグゼクティブサマリーにしてください。"
    ),
}


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    text = inputs["text"].strip()
    fmt = inputs.get("format", "3行まとめ")
    focus = inputs.get("focus", "").strip()

    lines = [_FORMAT_INSTRUCTIONS.get(fmt, _FORMAT_INSTRUCTIONS["3行まとめ"])]
    if focus:
        lines.append(f"特に「{focus}」の観点を重視してください。")
    lines += [
        "出力は日本語。原文が英語などでも日本語で要約します。",
        "",
        "--- 原文 ---",
        text,
    ]
    return _SYSTEM, "\n".join(lines)


register(
    Feature(
        key="summary",
        label="文章の要約",
        icon="📄",
        description="長い文章・議事録・記事を、指定した形式でコンパクトにまとめます。",
        temperature=0.3,
        fields=(
            Field(
                "text",
                "要約したい文章",
                kind="textarea",
                required=True,
                height=280,
            ),
            Field(
                "format",
                "出力形式",
                kind="select",
                options=tuple(_FORMAT_INSTRUCTIONS.keys()),
            ),
            Field(
                "focus",
                "重視する観点（任意）",
                placeholder="例: コスト影響 / 次のアクション",
            ),
        ),
        build_prompt=_build,
    )
)

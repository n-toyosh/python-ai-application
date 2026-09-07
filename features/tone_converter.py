"""文章のトーン・文体を変換する（言い換え）。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたはリライトの専門家です。元の文章の意味と情報を保ったまま、"
    "指定されたトーンや目的に合わせて言い換えます。"
)

_TARGETS = {
    "もっと丁寧・ビジネス向け": "敬語を整え、ビジネスの場にふさわしい丁寧な表現にしてください。",
    "もっとカジュアル・親しみやすく": "堅さを取り、話しかけるような親しみやすい表現にしてください。",
    "簡潔・要点だけ": "情報を保ったまま、短く歯切れよくしてください。",
    "やわらかく・角を立てない": "指摘や依頼の角を丸め、クッション言葉を使ってやわらかくしてください。",
    "説得力のある表現に": "根拠や利点が伝わるよう、説得力のある言い回しにしてください。",
    "英語に翻訳": "自然な英語に翻訳してください。直訳ではなく読みやすい英語に。",
}


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    text = inputs["text"].strip()
    target = inputs.get("target", next(iter(_TARGETS)))
    extra = inputs.get("extra", "").strip()

    lines = [_TARGETS.get(target, "")]
    if extra:
        lines.append(f"追加の要望: {extra}")
    lines += [
        "変換後の文章だけを出力してください（解説は不要）。",
        "",
        "--- 元の文章 ---",
        text,
    ]
    return _SYSTEM, "\n".join(lines)


register(
    Feature(
        key="tone",
        label="トーン変換・言い換え",
        icon="🎚️",
        description="同じ内容を、丁寧・カジュアル・簡潔・英訳などに書き換えます。",
        temperature=0.6,
        fields=(
            Field(
                "text",
                "変換したい文章",
                kind="textarea",
                required=True,
                height=200,
            ),
            Field(
                "target",
                "どう変えたいか",
                kind="select",
                options=tuple(_TARGETS.keys()),
            ),
            Field("extra", "追加の要望（任意）", placeholder="例: 絵文字は使わない / 200字以内"),
        ),
        build_prompt=_build,
    )
)

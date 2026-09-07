"""ブログ記事を執筆する。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは経験豊富な日本語ブログライターです。読者にとって具体的で実用的、"
    "かつ読みやすい記事を書きます。冗長な前置きや中身のない一般論は避け、"
    "見出し（##）と箇条書きを適切に使って構造化します。"
)


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    topic = inputs["topic"].strip()
    audience = inputs.get("audience", "").strip()
    tone = inputs.get("tone", "です・ます調（丁寧）")
    length = inputs.get("length", "普通（1500字前後）")
    keywords = inputs.get("keywords", "").strip()
    notes = inputs.get("notes", "").strip()

    lines = [
        "以下の条件でブログ記事を Markdown で執筆してください。",
        "",
        f"- テーマ: {topic}",
        f"- 文体: {tone}",
        f"- 分量の目安: {length}",
    ]
    if audience:
        lines.append(f"- 想定読者: {audience}")
    if keywords:
        lines.append(f"- 盛り込みたいキーワード: {keywords}")
    if notes:
        lines.append(f"- 補足・必ず触れてほしい内容: {notes}")
    lines += [
        "",
        "構成: 導入 → 本文（見出しで3〜5セクション）→ まとめ。",
        "タイトルは記事の先頭に # で1つ付けてください。",
    ]
    return _SYSTEM, "\n".join(lines)


register(
    Feature(
        key="blog",
        label="ブログ記事の執筆",
        icon="📝",
        description="テーマと条件から、見出し付きのブログ記事を丸ごと書き上げます。",
        temperature=0.8,
        fields=(
            Field(
                "topic",
                "記事のテーマ",
                kind="textarea",
                required=True,
                height=90,
                placeholder="例: 在宅ワークで集中力を保つための時間管理術",
            ),
            Field(
                "audience",
                "想定読者（任意）",
                placeholder="例: リモートワークを始めたばかりの会社員",
            ),
            Field(
                "tone",
                "文体",
                kind="select",
                options=(
                    "です・ます調（丁寧）",
                    "だ・である調（硬め）",
                    "カジュアル・親しみやすい",
                    "専門的・解説寄り",
                ),
            ),
            Field(
                "length",
                "分量",
                kind="select",
                options=(
                    "短め（800字前後）",
                    "普通（1500字前後）",
                    "長め（3000字前後）",
                ),
                default="普通（1500字前後）",
            ),
            Field("keywords", "キーワード（任意・カンマ区切り）", placeholder="時間管理, ポモドーロ, 集中"),
            Field(
                "notes",
                "補足・必ず触れてほしい点（任意）",
                kind="textarea",
                height=100,
            ),
        ),
        build_prompt=_build,
    )
)

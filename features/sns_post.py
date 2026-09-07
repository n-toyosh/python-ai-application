"""SNS 投稿文を生成する。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは SNS 運用に詳しいコピーライターです。各プラットフォームの文化と"
    "文字数感覚に合わせ、スクロールの手を止めさせる投稿文を書きます。"
    "誇張や事実誤認は避けます。"
)

_PLATFORM_HINTS = {
    "X (Twitter)": "140字を目安に。必要なら連続ポスト（スレッド）に分け、番号を振る。",
    "LinkedIn": "300〜600字。専門性と学びが伝わる落ち着いたトーン。改行を多めに。",
    "Instagram": "共感を軸にしたキャプション。最後に関連ハッシュタグを5〜10個。",
    "Facebook": "友人に語りかけるような自然な文体。長すぎない。",
}


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    topic = inputs["topic"].strip()
    platform = inputs.get("platform", "X (Twitter)")
    goal = inputs.get("goal", "情報をシェアして関心を持ってもらう")
    variations = int(inputs.get("variations", 3))
    hashtags = inputs.get("hashtags", "任せる")

    lines = [
        f"次のトピックについて {platform} 向けの投稿文を {variations} 案作ってください。",
        f"トピック: {topic}",
        f"投稿の目的: {goal}",
        f"ハッシュタグ: {hashtags}",
        _PLATFORM_HINTS.get(platform, ""),
        "",
        "各案を「案1」「案2」…と見出しで区切って出力してください。",
    ]
    return _SYSTEM, "\n".join(line for line in lines if line)


register(
    Feature(
        key="sns",
        label="SNS 投稿文の作成",
        icon="📣",
        description="トピックとプラットフォームを指定して、投稿文を複数案つくります。",
        temperature=0.9,
        fields=(
            Field(
                "topic",
                "投稿したい内容・伝えたいこと",
                kind="textarea",
                required=True,
                height=120,
            ),
            Field(
                "platform",
                "プラットフォーム",
                kind="select",
                options=tuple(_PLATFORM_HINTS.keys()),
            ),
            Field(
                "goal",
                "投稿の目的",
                kind="select",
                options=(
                    "情報をシェアして関心を持ってもらう",
                    "記事・製品ページへ誘導する",
                    "議論・コメントを促す",
                    "自分の考えや実績を発信する",
                ),
            ),
            Field("variations", "案の数", kind="slider", min=1, max=5, step=1, default=3),
            Field(
                "hashtags",
                "ハッシュタグの方針",
                kind="select",
                options=("任せる", "付けない", "3個まで", "多め（5〜10個）"),
            ),
        ),
        build_prompt=_build,
    )
)

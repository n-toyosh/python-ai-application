"""受信メールに対する返信文を作成する。"""

from __future__ import annotations

from typing import Any

from ai_core import Feature, Field, register

_SYSTEM = (
    "あなたは日本語ビジネスメールの作成に長けたアシスタントです。"
    "相手との関係性と目的に合わせて、過不足なく礼儀正しい返信を書きます。"
    "定型の挨拶は簡潔にし、要件が明確に伝わる構成にします。"
)


def _build(inputs: dict[str, Any]) -> tuple[str, str]:
    received = inputs["received"].strip()
    intent = inputs["intent"].strip()
    relationship = inputs.get("relationship", "社外の取引先")
    tone = inputs.get("tone", "丁寧・標準")
    my_name = inputs.get("my_name", "").strip()

    lines = [
        "次の受信メールに対する返信文を作成してください。",
        "",
        "--- 受信メール ---",
        received,
        "--- ここまで ---",
        "",
        f"返信で伝えたいこと・目的: {intent}",
        f"相手との関係: {relationship}",
        f"トーン: {tone}",
    ]
    if my_name:
        lines.append(f"差出人（自分）の署名に使う名前: {my_name}")
    lines += [
        "",
        "件名（Re: を含む）、本文の順で出力してください。",
        "推測で事実を作らず、埋めるべき箇所は [ ] のプレースホルダにしてください。",
    ]
    return _SYSTEM, "\n".join(lines)


register(
    Feature(
        key="email",
        label="メール返信文の作成",
        icon="✉️",
        description="受信メールと返信の意図を入力すると、返信文の下書きを作ります。",
        temperature=0.5,
        fields=(
            Field(
                "received",
                "受信したメールの本文",
                kind="textarea",
                required=True,
                height=200,
            ),
            Field(
                "intent",
                "返信で伝えたいこと",
                kind="textarea",
                required=True,
                height=110,
                placeholder="例: 提案は前向きに検討したい。ただし納期を1週間延ばせるか確認したい。",
            ),
            Field(
                "relationship",
                "相手との関係",
                kind="select",
                options=(
                    "社外の取引先",
                    "社外・初めて連絡する相手",
                    "社内の上司",
                    "社内の同僚・部下",
                    "顧客・お客様",
                ),
            ),
            Field(
                "tone",
                "トーン",
                kind="select",
                options=("丁寧・標準", "かなり丁寧・かしこまり", "簡潔・事務的", "やわらかく友好的"),
            ),
            Field("my_name", "署名に使う自分の名前（任意）", placeholder="例: 山田"),
        ),
        build_prompt=_build,
    )
)

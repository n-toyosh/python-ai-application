"""ライティング機能のレジストリ。

新しい機能を足す手順:
1. `features/` に 1 ファイル作る
2. `Feature(...)` を組み立てて `register()` に渡す
3. `features/__init__.py` にインポートを 1 行足す
これだけで UI のメニューに出てくる。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

import config

FieldKind = Literal["text", "textarea", "select", "slider"]


@dataclass(frozen=True)
class Field:
    """機能ごとの入力欄 1 つ分の定義。Streamlit のウィジェットに対応する。"""

    key: str
    label: str
    kind: FieldKind = "text"
    required: bool = False
    help: str | None = None
    placeholder: str = ""
    default: Any = None
    # select 用
    options: tuple[str, ...] = ()
    # slider 用
    min: float = 0.0
    max: float = 1.0
    step: float = 0.1
    # textarea 用
    height: int = 160


# build_prompt は入力 dict を受け取り (system_instruction, user_prompt) を返す。
PromptBuilder = Callable[[dict[str, Any]], tuple[str, str]]


@dataclass(frozen=True)
class Feature:
    key: str
    label: str
    icon: str
    description: str
    fields: tuple[Field, ...]
    build_prompt: PromptBuilder
    temperature: float = config.DEFAULT_TEMPERATURE
    max_output_tokens: int = config.DEFAULT_MAX_OUTPUT_TOKENS

    @property
    def menu_label(self) -> str:
        return f"{self.icon}  {self.label}"


_REGISTRY: dict[str, Feature] = {}


def register(feature: Feature) -> Feature:
    if feature.key in _REGISTRY:
        raise ValueError(f"機能キーが重複しています: {feature.key}")
    _REGISTRY[feature.key] = feature
    return feature


def all_features() -> list[Feature]:
    return list(_REGISTRY.values())


def get_feature(key: str) -> Feature:
    return _REGISTRY[key]

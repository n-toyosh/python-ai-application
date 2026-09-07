"""Gemini API の薄いラッパー。

google-genai SDK (`from google import genai`) を使う。
各機能モジュールはここの `generate` / `generate_stream` だけを呼べばよい。
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from functools import lru_cache

from google import genai
from google.genai import types

import config

_log = logging.getLogger(__name__)


class GeminiError(RuntimeError):
    """API キー未設定や API 呼び出し失敗をまとめて表す。"""


def _user_message(exc: Exception) -> str:
    """SDK 例外を、UI に出しても安全な短いメッセージに変換する。

    生の例外文字列にはエンドポイント URL・リクエスト ID・プロジェクト情報などが
    含まれることがあるため UI には出さない（詳細はサーバーログにのみ記録）。
    """
    text = str(exc).lower()
    if any(s in text for s in ("api key", "api_key", "unauthenticated", "permission denied", "401", "403")):
        return "API キーが無効か、権限がありません。キーを確認してください。"
    if any(s in text for s in ("resource_exhausted", "rate limit", "quota", "429")):
        return "API のレート上限に達しました。しばらく待ってから再試行してください。"
    if any(s in text for s in ("not found", "404", "is not supported", "unsupported")):
        return "指定したモデルが利用できません。サイドバーで別のモデルを選んでください。"
    if any(s in text for s in ("deadline exceeded", "timeout", "timed out", "unavailable", "connection")):
        return "API への接続に失敗しました。ネットワークを確認して再試行してください。"
    return "生成に失敗しました。時間をおいて、モデルや入力を変えて再試行してください。"


def resolve_api_key(explicit: str | None = None) -> str | None:
    """明示指定 → 環境変数 → .env の順で API キーを解決する。"""
    if explicit and explicit.strip():
        return explicit.strip()
    for name in config.API_KEY_ENV_VARS:
        value = os.environ.get(name)
        if value and value.strip():
            return value.strip()
    return None


# maxsize=1: 直近で使ったキーの Client だけを保持する。
# 大きくすると複数の API キー文字列がプロセスメモリに長く滞留する
# （マルチユーザー運用時に他人のキーが残るリスク）。
@lru_cache(maxsize=1)
def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _build_config(
    system_instruction: str | None,
    temperature: float,
    max_output_tokens: int,
) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=system_instruction or None,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        # このアプリはツール呼び出しを使わないので自動関数呼び出しを無効化
        # （SDK の警告も抑制される）
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


def generate(
    prompt: str,
    *,
    api_key: str,
    model: str = config.DEFAULT_MODEL,
    system_instruction: str | None = None,
    temperature: float = config.DEFAULT_TEMPERATURE,
    max_output_tokens: int = config.DEFAULT_MAX_OUTPUT_TOKENS,
) -> str:
    """一括生成。テキスト全体を文字列で返す。"""
    key = resolve_api_key(api_key)
    if not key:
        raise GeminiError("API キーが設定されていません。")
    try:
        response = _client(key).models.generate_content(
            model=model,
            contents=prompt,
            config=_build_config(system_instruction, temperature, max_output_tokens),
        )
    except Exception as exc:  # SDK の例外階層はバージョンで揺れるのでまとめて包む
        _log.exception("Gemini generate_content failed")
        raise GeminiError(_user_message(exc)) from exc

    text = getattr(response, "text", None)
    if not text:
        raise GeminiError("モデルから空の応答が返りました。プロンプトや設定を見直してください。")
    return text


def generate_stream(
    prompt: str,
    *,
    api_key: str,
    model: str = config.DEFAULT_MODEL,
    system_instruction: str | None = None,
    temperature: float = config.DEFAULT_TEMPERATURE,
    max_output_tokens: int = config.DEFAULT_MAX_OUTPUT_TOKENS,
) -> Iterator[str]:
    """ストリーミング生成。テキストの断片を順次 yield する。"""
    key = resolve_api_key(api_key)
    if not key:
        raise GeminiError("API キーが設定されていません。")
    try:
        stream = _client(key).models.generate_content_stream(
            model=model,
            contents=prompt,
            config=_build_config(system_instruction, temperature, max_output_tokens),
        )
        for chunk in stream:
            piece = getattr(chunk, "text", None)
            if piece:
                yield piece
    except GeminiError:
        raise
    except Exception as exc:
        _log.exception("Gemini generate_content_stream failed")
        raise GeminiError(_user_message(exc)) from exc

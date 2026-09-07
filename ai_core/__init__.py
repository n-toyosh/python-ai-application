"""Gemini 呼び出しと機能レジストリの共通コア。"""

from ai_core.client import GeminiError, generate, generate_stream, resolve_api_key
from ai_core.registry import Feature, Field, all_features, get_feature, register

__all__ = [
    "GeminiError",
    "generate",
    "generate_stream",
    "resolve_api_key",
    "Feature",
    "Field",
    "all_features",
    "get_feature",
    "register",
]

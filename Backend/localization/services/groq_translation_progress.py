from __future__ import annotations

from typing import Any

from django.core.cache import cache

from localization.services.groq_translation_runner import LOCK_TTL


def groq_progress_key(handler: str) -> str:
    return f"groq_translate_progress:{handler}"


def get_groq_translation_progress(handler: str) -> dict[str, Any] | None:
    payload = cache.get(groq_progress_key(handler))
    return payload if isinstance(payload, dict) else None


class GroqTranslationProgress:
    def __init__(self, handler: str):
        self.handler = handler
        self.key = groq_progress_key(handler)

    def init(self, total: int) -> None:
        cache.set(
            self.key,
            {
                "status": "running",
                "total": max(total, 0),
                "current": 0,
                "percent": 0,
                "label": "Hazirlaniyor…",
                "errors": [],
            },
            LOCK_TTL,
        )

    def advance(self, *, label: str, error: str | None = None) -> None:
        data = cache.get(self.key) or {}
        total = max(int(data.get("total", 0)), 1)
        current = int(data.get("current", 0)) + 1
        errors = list(data.get("errors", []))
        if error:
            errors.append(error)
            if len(errors) > 20:
                errors = errors[-20:]
        cache.set(
            self.key,
            {
                "status": "running",
                "total": total,
                "current": current,
                "percent": min(100, int(current * 100 / total)),
                "label": label,
                "errors": errors,
            },
            LOCK_TTL,
        )

    def finish(
        self,
        *,
        stats: dict[str, int] | None = None,
        error: str | None = None,
    ) -> None:
        data = cache.get(self.key) or {}
        total = int(data.get("total", 0))
        current = int(data.get("current", 0))
        percent = 100 if not error else int(data.get("percent", 0))
        cache.set(
            self.key,
            {
                "status": "error" if error else "done",
                "total": total,
                "current": current,
                "percent": percent,
                "label": error or "Tamamlandi.",
                "errors": list(data.get("errors", [])),
                "stats": stats,
                "error": error,
            },
            LOCK_TTL,
        )

    def clear(self) -> None:
        cache.delete(self.key)

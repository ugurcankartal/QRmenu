import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.cache import cache

LOCK_TTL = 7200
RESULT_TTL = 86400


def groq_lock_key(handler: str) -> str:
    return f"groq_translate_lock:{handler}"


def groq_result_key(handler: str) -> str:
    return f"groq_translate_result:{handler}"


def is_groq_translation_running(handler: str) -> bool:
    if cache.get(groq_lock_key(handler)):
        return True
    progress = cache.get(f"groq_translate_progress:{handler}")
    return isinstance(progress, dict) and progress.get("status") == "running"


def get_groq_translation_status(handler: str) -> dict[str, Any] | None:
    payload = cache.get(groq_result_key(handler))
    return payload if isinstance(payload, dict) else None


def save_groq_translation_result(
    handler: str,
    *,
    stats: dict[str, int] | None = None,
    error: str | None = None,
) -> None:
    cache.set(
        groq_result_key(handler),
        {
            "stats": stats,
            "error": error,
        },
        RESULT_TTL,
    )


def start_groq_translation_background(handler: str) -> str:
    if is_groq_translation_running(handler):
        return "already_running"

    from localization.services.groq_translation_progress import GroqTranslationProgress

    GroqTranslationProgress(handler).init(0)

    backend_dir = Path(settings.BASE_DIR)
    manage_py = backend_dir / "manage.py"
    logs_dir = backend_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / f"groq-{handler}.log"

    env = os.environ.copy()
    env.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.prod"),
    )

    python = sys.executable
    venv_python = backend_dir / "venv" / "bin" / "python"
    if venv_python.is_file():
        python = str(venv_python)

    try:
        log_file = open(log_path, "a", encoding="utf-8")
        subprocess.Popen(
            [python, str(manage_py), "groq_translate", handler],
            cwd=str(backend_dir),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError:
        return "spawn_error"

    return "started"

from django.core.cache import cache
from django.core.management.base import BaseCommand

from core.groq_client import GroqAPIError
from localization.services.groq_translation import (
    HANDLERS,
    public_groq_stats,
    run_groq_translation,
)
from localization.services.groq_translation_progress import GroqTranslationProgress
from localization.services.groq_translation_runner import (
    LOCK_VALUE_RUNNING,
    LOCK_VALUE_STARTING,
    acquire_groq_lock,
    groq_lock_key,
    promote_groq_lock_to_running,
    release_groq_lock,
    save_groq_translation_result,
)


class Command(BaseCommand):
    help = "Groq ile eksik cevirileri arka planda tamamlar."

    def add_arguments(self, parser):
        parser.add_argument(
            "handler",
            choices=sorted(HANDLERS.keys()),
        )

    def handle(self, *args, **options):
        handler = options["handler"]
        lock_key = groq_lock_key(handler)
        progress = GroqTranslationProgress(handler)

        lock_state = cache.get(lock_key)
        if lock_state == LOCK_VALUE_STARTING:
            promote_groq_lock_to_running(handler)
        elif not acquire_groq_lock(handler, source="cli"):
            self.stdout.write("Groq cevirisi zaten calisiyor.")
            return

        progress.init(0)

        try:
            stats = run_groq_translation(handler, progress=progress)
            public_stats = public_groq_stats(stats)
            warning = stats.get("_abort_message")
            progress.finish(stats=public_stats, warning=warning)
            save_groq_translation_result(handler, stats=public_stats, error=warning)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Tamamlandi: {public_stats.get('created', 0)} yeni, "
                    f"{public_stats.get('updated', 0)} guncellendi, "
                    f"{public_stats.get('skipped', 0)} atlandi, "
                    f"{public_stats.get('failed', 0)} hata."
                )
            )
            if warning:
                self.stdout.write(self.style.WARNING(warning))
        except (GroqAPIError, ValueError) as exc:
            progress.finish(error=str(exc))
            save_groq_translation_result(handler, error=str(exc))
            self.stderr.write(str(exc))
        except Exception as exc:
            progress.finish(error=str(exc))
            save_groq_translation_result(handler, error=str(exc))
            raise
        finally:
            release_groq_lock(handler)

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from core.groq_client import GroqAPIError
from localization.services.groq_translation import HANDLERS, run_groq_translation
from localization.services.groq_translation_runner import (
    LOCK_TTL,
    groq_lock_key,
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

        if not cache.add(lock_key, "1", LOCK_TTL):
            self.stdout.write("Groq cevirisi zaten calisiyor.")
            return

        try:
            stats = run_groq_translation(handler)
            save_groq_translation_result(handler, stats=stats)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Tamamlandi: {stats.get('created', 0)} yeni, "
                    f"{stats.get('skipped', 0)} atlandi."
                )
            )
        except (GroqAPIError, ValueError) as exc:
            save_groq_translation_result(handler, error=str(exc))
            raise CommandError(str(exc)) from exc
        except Exception as exc:
            save_groq_translation_result(handler, error=str(exc))
            raise
        finally:
            cache.delete(lock_key)

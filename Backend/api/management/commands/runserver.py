from django.conf import settings

try:
    from django.contrib.staticfiles.management.commands.runserver import (
        Command as BaseRunserverCommand,
    )
except ImportError:
    from django.core.management.commands.runserver import (
        Command as BaseRunserverCommand,
    )


class Command(BaseRunserverCommand):
    def handle(self, *args, **options):
        if not options.get("addrport"):
            host = getattr(settings, "RUNSERVER_HOST", "127.0.0.1")
            port = getattr(settings, "RUNSERVER_PORT", "8000")
            options["addrport"] = f"{host}:{port}"
        return super().handle(*args, **options)
import os

from .base import *  # noqa: F403

DEBUG = env_bool("DJANGO_DEBUG", True)  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DEV_DB_NAME", ""),
        "USER": os.getenv("DEV_DB_USER", ""),
        "PASSWORD": os.getenv("DEV_DB_PASSWORD", ""),
        "HOST": os.getenv("DEV_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DEV_DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("DEV_EMAIL_HOST", "localhost")
EMAIL_PORT = env_int("DEV_EMAIL_PORT", 587)  # noqa: F405
EMAIL_HOST_USER = os.getenv("DEV_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("DEV_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("DEV_EMAIL_USE_TLS", True)  # noqa: F405
DEFAULT_FROM_EMAIL = os.getenv("DEV_DEFAULT_FROM_EMAIL", "webmaster@localhost")

RUNSERVER_HOST = os.getenv("DEV_RUNSERVER_HOST", "127.0.0.1")
RUNSERVER_PORT = os.getenv("DEV_RUNSERVER_PORT", "8000")

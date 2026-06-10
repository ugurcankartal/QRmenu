import os

from .base import *  # noqa: F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("PROD_DB_NAME", ""),
        "USER": os.getenv("PROD_DB_USER", ""),
        "PASSWORD": os.getenv("PROD_DB_PASSWORD", ""),
        "HOST": os.getenv("PROD_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("PROD_DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("PROD_EMAIL_HOST", "localhost")
EMAIL_PORT = env_int("PROD_EMAIL_PORT", 587)  # noqa: F405
EMAIL_HOST_USER = os.getenv("PROD_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("PROD_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("PROD_EMAIL_USE_TLS", True)  # noqa: F405
DEFAULT_FROM_EMAIL = os.getenv("PROD_DEFAULT_FROM_EMAIL", "webmaster@localhost")

RUNSERVER_HOST = os.getenv("PROD_RUNSERVER_HOST", "0.0.0.0")
RUNSERVER_PORT = os.getenv("PROD_RUNSERVER_PORT", "8000")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

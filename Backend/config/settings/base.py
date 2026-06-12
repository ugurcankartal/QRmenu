import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in {"true", "1", "yes", "on"}


def env_list(key: str, default: str = "") -> list[str]:
    value = os.getenv(key, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def env_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    return int(value)


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in .env")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "api",
    "security",
    "core",
    "localization",
    "currency",
    "adisyon",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "mptt",
    "django_ckeditor_5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "security.middleware.SqlInjectionDetectionMiddleware",
    "api.middleware.FrontendAccessMiddleware",
    "security.middleware.SiteVisitLoggingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
}

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:25489,http://127.0.0.1:25489,"
    "http://localhost:48256,http://127.0.0.1:48256",
)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:25489,http://127.0.0.1:25489,"
    "http://localhost:25490,http://127.0.0.1:25490",
)
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-session-key",
)
CORS_EXPOSE_HEADERS = ["X-Session-Key"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_5_COLOR_PALETTE = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
    {"color": "hsl(145, 63%, 42%)", "label": "Green"},
    {"color": "hsl(36, 100%, 50%)", "label": "Orange"},
    {"color": "hsl(0, 0%, 0%)", "label": "Black"},
    {"color": "hsl(0, 0%, 100%)", "label": "White"},
]

CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

CKEDITOR_5_CONFIGS = {
    "campaign_description": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": {
            "items": [
                "undo",
                "redo",
                "|",
                "selectAll",
                "findAndReplace",
                "showBlocks",
                "|",
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "alignment",
                "|",
                "bold",
                "italic",
                "underline",
                "strikethrough",
                "code",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "link",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "|",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "blockQuote",
                "codeBlock",
                "horizontalLine",
                "pageBreak",
                "|",
                "insertImage",
                "imageUpload",
                "mediaEmbed",
                "htmlEmbed",
                "|",
                "insertTable",
                "|",
                "specialCharacters",
                "|",
                "sourceEditing",
                "removeFormat",
            ],
            "shouldNotGroupWhenFull": True,
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "imageStyle:side",
                "|",
                "toggleImageCaption",
                "linkImage",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": CKEDITOR_5_COLOR_PALETTE,
                "backgroundColors": CKEDITOR_5_COLOR_PALETTE,
            },
            "tableCellProperties": {
                "borderColors": CKEDITOR_5_COLOR_PALETTE,
                "backgroundColors": CKEDITOR_5_COLOR_PALETTE,
            },
        },
        "fontSize": {
            "options": [
                8,
                9,
                10,
                11,
                12,
                14,
                "default",
                16,
                18,
                20,
                22,
                24,
                26,
                28,
                32,
                36,
                48,
                72,
            ],
            "supportAllValues": True,
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraf",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Başlık 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Başlık 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Başlık 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": "h4",
                    "title": "Başlık 4",
                    "class": "ck-heading_heading4",
                },
            ],
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True,
            },
        },
        "language": "tr",
    },
}

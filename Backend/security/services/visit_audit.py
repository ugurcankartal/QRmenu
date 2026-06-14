from django.core.cache import cache
from django.http import HttpRequest

from security.models import SitePageVisit
from security.services.client_fingerprint import build_client_fingerprint, pick_model_fields

VISIT_THROTTLE_SECONDS = 30
SESSION_HEADER = "X-Session-Key"
SESSION_COOKIE = "adisyon_session"
SKIP_PAGE_PATH_PREFIXES = (
    "/static/",
    "/media/",
    "/api/",
    "/admin/",
    "/ckeditor5/",
)


def normalize_page_path(path: str) -> str:
    normalized = (path or "/").strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized[:512]


def should_log_page_visit(request: HttpRequest, page_path: str) -> bool:
    if request.method not in {"GET", "POST"}:
        return False

    path = normalize_page_path(page_path)
    if any(path.startswith(prefix) for prefix in SKIP_PAGE_PATH_PREFIXES):
        return False

    fingerprint = build_client_fingerprint(request)
    ip_address = fingerprint.get("ip_address") or "unknown"
    cache_key = f"pagevisit:{ip_address}:{path}"
    if cache.get(cache_key):
        return False
    cache.set(cache_key, 1, VISIT_THROTTLE_SECONDS)
    return True


def resolve_session_key_from_request(request: HttpRequest):
    from adisyon.models import SessionKey

    raw_key = request.headers.get(SESSION_HEADER) or request.COOKIES.get(SESSION_COOKIE)
    if not raw_key:
        return None
    return SessionKey.objects.filter(key=raw_key).first()


def resolve_adisyon_for_session_key(session_key):
    if session_key is None:
        return None

    from adisyon.models import Adisyon

    return Adisyon.objects.filter(session_key=session_key).first()


def log_site_page_visit(
    request: HttpRequest,
    *,
    page_path: str,
    visit_source: str = SitePageVisit.VisitSource.FRONTEND_ROUTE,
    referer: str = "",
    query_string: str = "",
    user=None,
) -> SitePageVisit | None:
    path = normalize_page_path(page_path)
    if not should_log_page_visit(request, path):
        return None

    fingerprint = pick_model_fields(
        SitePageVisit,
        build_client_fingerprint(request),
    )
    security_headers = fingerprint.pop("security_headers", {})
    stored_query = (query_string or request.META.get("QUERY_STRING", ""))[:512]

    if referer:
        fingerprint["referer"] = referer[:2000]
    elif not fingerprint.get("referer"):
        fingerprint["referer"] = request.META.get("HTTP_REFERER", "")[:2000]

    resolved_user = user
    if resolved_user is None and getattr(request, "user", None) and request.user.is_authenticated:
        resolved_user = request.user

    session_key = resolve_session_key_from_request(request)
    adisyon = resolve_adisyon_for_session_key(session_key)

    return SitePageVisit.objects.create(
        page_path=path,
        query_string=stored_query,
        visit_source=visit_source,
        user=resolved_user,
        session_key=session_key,
        adisyon=adisyon,
        security_headers=security_headers,
        **fingerprint,
    )

import re
from typing import Iterator

from django.http import HttpRequest, QueryDict

from security.models import SqlInjectionAttempt
from security.services.client_fingerprint import (
    build_client_fingerprint,
    pick_model_fields,
    safe_json_preview,
    truncate_text,
)

SQL_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("union_select", re.compile(r"\bunion\b[\s/\*]*\bselect\b", re.IGNORECASE)),
    ("or_1_equals_1", re.compile(r"\b(or|and)\b\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?", re.IGNORECASE)),
    ("sleep_wait", re.compile(r"\b(sleep|benchmark|waitfor\s+delay)\b\s*\(", re.IGNORECASE)),
    ("drop_table", re.compile(r"\bdrop\b\s+(table|database|schema)\b", re.IGNORECASE)),
    ("information_schema", re.compile(r"\binformation_schema\b", re.IGNORECASE)),
    ("exec_xp", re.compile(r"\b(exec|execute|xp_cmdshell|sp_executesql)\b", re.IGNORECASE)),
    ("insert_into", re.compile(r"\binsert\b\s+into\b", re.IGNORECASE)),
    ("delete_from", re.compile(r"\bdelete\b\s+from\b", re.IGNORECASE)),
    ("update_set", re.compile(r"\bupdate\b\s+\w+\s+set\b", re.IGNORECASE)),
    ("load_file", re.compile(r"\bload_file\s*\(", re.IGNORECASE)),
    ("into_outfile", re.compile(r"\binto\b\s+(outfile|dumpfile)\b", re.IGNORECASE)),
    ("sql_hex", re.compile(r"0x[0-9a-f]{8,}", re.IGNORECASE)),
)

MAX_SCAN_LENGTH = 4096
SKIP_PATH_PREFIXES = (
    "/static/",
    "/media/",
)


def _iter_values(source: str, data: QueryDict) -> Iterator[tuple[str, str]]:
    for key in data:
        for value in data.getlist(key):
            yield f"{source}:{key}", str(value)


def _iter_request_values(request: HttpRequest) -> Iterator[tuple[str, str]]:
    yield "path", request.path
    if request.META.get("QUERY_STRING"):
        yield "query_string", request.META["QUERY_STRING"]

    yield from _iter_values("GET", request.GET)

    content_type = request.META.get("CONTENT_TYPE", "")
    if "application/json" in content_type and request.body:
        yield "body", request.body.decode("utf-8", errors="replace")[:MAX_SCAN_LENGTH]
    elif request.method in {"POST", "PUT", "PATCH"}:
        yield from _iter_values("POST", request.POST)


def find_sql_injection_match(request: HttpRequest) -> tuple[str, str, str] | None:
    for source, value in _iter_request_values(request):
        snippet = truncate_text(value, MAX_SCAN_LENGTH)
        if not snippet.strip():
            continue
        for pattern_name, pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(snippet):
                return pattern_name, snippet, source
    return None


def record_sql_injection_attempt(
    request: HttpRequest,
    *,
    matched_pattern: str,
    matched_value: str,
    source: str,
) -> SqlInjectionAttempt:
    fingerprint = pick_model_fields(
        SqlInjectionAttempt,
        build_client_fingerprint(request),
    )
    security_headers = fingerprint.pop("security_headers", {})
    return SqlInjectionAttempt.objects.create(
        matched_pattern=matched_pattern[:255],
        matched_value=truncate_text(matched_value, 2000),
        source=source[:64],
        query_string=truncate_text(request.META.get("QUERY_STRING", ""), 2000),
        request_body=safe_json_preview(
            request.body.decode("utf-8", errors="replace")[:MAX_SCAN_LENGTH]
            if request.body
            else ""
        ),
        security_headers=security_headers,
        **fingerprint,
    )


def should_scan_request(request: HttpRequest) -> bool:
    path = request.path
    return not any(path.startswith(prefix) for prefix in SKIP_PATH_PREFIXES)

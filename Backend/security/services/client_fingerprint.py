import json
import re
from typing import Any

from django.http import HttpRequest

COUNTRY_NAMES = {
    "TR": "Turkiye",
    "US": "United States",
    "DE": "Germany",
    "GB": "United Kingdom",
    "FR": "France",
    "NL": "Netherlands",
    "RU": "Russia",
    "CN": "China",
}

SECURITY_HEADER_KEYS = (
    "HTTP_CF_RAY",
    "HTTP_CF_CONNECTING_IP",
    "HTTP_CF_IPCOUNTRY",
    "HTTP_CF_IPCITY",
    "HTTP_CF_REGION",
    "HTTP_CF_POSTAL_CODE",
    "HTTP_CF_TIMEZONE",
    "HTTP_X_FORWARDED_FOR",
    "HTTP_X_FORWARDED_PROTO",
    "HTTP_X_REAL_IP",
    "HTTP_ORIGIN",
    "HTTP_SEC_CH_UA",
    "HTTP_SEC_CH_UA_MOBILE",
    "HTTP_SEC_CH_UA_PLATFORM",
    "HTTP_SEC_FETCH_SITE",
    "HTTP_SEC_FETCH_MODE",
    "HTTP_SEC_FETCH_DEST",
)


def _first_ip(value: str) -> str:
    if not value:
        return ""
    return value.split(",")[0].strip()


def get_client_ip(request: HttpRequest) -> str:
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP", "").strip()
    if cf_ip:
        return cf_ip
    real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
    if real_ip:
        return _first_ip(real_ip)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").strip()
    if forwarded:
        return _first_ip(forwarded)
    return request.META.get("REMOTE_ADDR", "") or ""


def get_forwarded_for(request: HttpRequest) -> str:
    return request.META.get("HTTP_X_FORWARDED_FOR", "").strip()


def _parse_user_agent(user_agent: str) -> dict[str, str]:
    ua = user_agent or ""
    lowered = ua.lower()
    result = {
        "browser_name": "",
        "browser_version": "",
        "os_name": "",
        "os_version": "",
        "device_type": "desktop",
        "device_brand": "",
        "device_model": "",
        "is_mobile": False,
        "is_bot": False,
    }

    if not ua:
        return result

    if any(token in lowered for token in ("bot", "spider", "crawl", "slurp")):
        result["is_bot"] = True
        result["device_type"] = "bot"

    if "mobile" in lowered or "android" in lowered or "iphone" in lowered:
        result["is_mobile"] = True
        result["device_type"] = "mobile"
    elif "ipad" in lowered or "tablet" in lowered:
        result["is_mobile"] = True
        result["device_type"] = "tablet"

    browser_patterns = (
        ("Edge", r"Edg/([\d.]+)"),
        ("Chrome", r"Chrome/([\d.]+)"),
        ("Firefox", r"Firefox/([\d.]+)"),
        ("Safari", r"Version/([\d.]+).*Safari"),
        ("Opera", r"OPR/([\d.]+)"),
    )
    for name, pattern in browser_patterns:
        match = re.search(pattern, ua)
        if match:
            result["browser_name"] = name
            result["browser_version"] = match.group(1)
            break

    os_patterns = (
        ("Windows", r"Windows NT ([\d.]+)"),
        ("macOS", r"Mac OS X ([\d_]+)"),
        ("Android", r"Android ([\d.]+)"),
        ("iOS", r"CPU (?:iPhone )?OS ([\d_]+)"),
        ("Linux", r"Linux"),
    )
    for name, pattern in os_patterns:
        match = re.search(pattern, ua)
        if match:
            result["os_name"] = name
            if match.lastindex:
                result["os_version"] = match.group(1).replace("_", ".")
            break

    android_model = re.search(r"Android[^;]*;\s([^;)]+)\)", ua)
    if android_model:
        result["device_brand"] = android_model.group(1).strip()
        result["device_model"] = result["device_brand"]

    iphone_match = re.search(r"\((iPhone[^;)]+)\)", ua)
    if iphone_match:
        result["device_brand"] = "Apple"
        result["device_model"] = iphone_match.group(1).strip()

    return result


def _geo_from_request(request: HttpRequest) -> dict[str, Any]:
    country_code = (
        request.META.get("HTTP_CF_IPCOUNTRY", "")
        or request.META.get("HTTP_X_APPENGINE_COUNTRY", "")
    ).strip()[:8]
    city = request.META.get("HTTP_CF_IPCITY", "").strip()[:120]
    region = request.META.get("HTTP_CF_REGION", "").strip()[:120]
    postal_code = request.META.get("HTTP_CF_POSTAL_CODE", "").strip()[:32]

    country_name = COUNTRY_NAMES.get(country_code.upper(), country_code)

    parts = [part for part in (city, region, country_name) if part]
    location_label = ", ".join(parts)

    latitude = None
    longitude = None

    return {
        "country_code": country_code,
        "country_name": country_name,
        "city": city,
        "region": region,
        "postal_code": postal_code,
        "latitude": latitude,
        "longitude": longitude,
        "location_label": location_label,
    }


def collect_security_headers(request: HttpRequest) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key in SECURITY_HEADER_KEYS:
        value = request.META.get(key, "")
        if value:
            headers[key.removeprefix("HTTP_").replace("_", "-")] = str(value)[:500]
    return headers


def build_client_fingerprint(request: HttpRequest) -> dict[str, Any]:
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    ua_data = _parse_user_agent(user_agent)
    geo = _geo_from_request(request)

    return {
        "ip_address": get_client_ip(request) or None,
        "forwarded_for": get_forwarded_for(request),
        "user_agent": user_agent[:2000],
        "accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE", "")[:255],
        "referer": request.META.get("HTTP_REFERER", "")[:2000],
        "host": request.get_host()[:255],
        "request_method": request.method,
        "request_path": request.path[:512],
        "is_secure": request.is_secure(),
        "security_headers": collect_security_headers(request),
        **geo,
        **ua_data,
    }


def truncate_text(value: str, limit: int = 2000) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def safe_json_preview(data: Any, limit: int = 2000) -> str:
    try:
        encoded = json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        encoded = str(data)
    return truncate_text(encoded, limit)


def pick_model_fields(model, data: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        field.name
        for field in model._meta.fields
        if not field.auto_created or field.concrete
    }
    return {key: value for key, value in data.items() if key in allowed}

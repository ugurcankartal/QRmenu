import ipaddress
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from django.core.cache import cache
from django.http import HttpRequest

IP_GEO_CACHE_TTL = 86400
IP_GEO_LOOKUP_TIMEOUT = 2

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
    "HTTP_CF_REGION_CODE",
    "HTTP_CF_POSTAL_CODE",
    "HTTP_CF_IPLATITUDE",
    "HTTP_CF_IPLONGITUDE",
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


def _parse_coordinate(value: str) -> Decimal | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def _is_public_ip(ip: str) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
    )


def _build_location_label(
    *,
    city: str,
    region: str,
    postal_code: str,
    country_name: str,
) -> str:
    parts: list[str] = []
    if city:
        parts.append(city)
    if region and region != city:
        parts.append(region)
    if postal_code:
        parts.append(postal_code)
    if country_name:
        parts.append(country_name)
    return ", ".join(parts)


def _lookup_ip_geolocation(ip: str) -> dict[str, Any]:
    cache_key = f"ipgeo:{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    empty: dict[str, Any] = {
        "country_code": "",
        "country_name": "",
        "city": "",
        "region": "",
        "postal_code": "",
        "latitude": None,
        "longitude": None,
    }
    if not _is_public_ip(ip):
        cache.set(cache_key, empty, IP_GEO_CACHE_TTL)
        return empty

    try:
        url = (
            f"http://ip-api.com/json/{ip}"
            "?fields=status,country,countryCode,regionName,city,zip,lat,lon"
        )
        with urlopen(url, timeout=IP_GEO_LOOKUP_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        cache.set(cache_key, empty, IP_GEO_CACHE_TTL // 4)
        return empty

    if payload.get("status") != "success":
        cache.set(cache_key, empty, IP_GEO_CACHE_TTL // 4)
        return empty

    country_code = (payload.get("countryCode") or "")[:8]
    country_name = (payload.get("country") or "")[:100]
    if not country_name and country_code:
        country_name = COUNTRY_NAMES.get(country_code.upper(), country_code)

    result = {
        "country_code": country_code,
        "country_name": country_name,
        "city": (payload.get("city") or "")[:120],
        "region": (payload.get("regionName") or "")[:120],
        "postal_code": (payload.get("zip") or "")[:32],
        "latitude": _parse_coordinate(str(payload.get("lat", ""))),
        "longitude": _parse_coordinate(str(payload.get("lon", ""))),
    }
    cache.set(cache_key, result, IP_GEO_CACHE_TTL)
    return result


def _merge_geo_value(primary: Any, fallback: Any) -> Any:
    if primary not in (None, ""):
        return primary
    return fallback


def _geo_from_request(request: HttpRequest) -> dict[str, Any]:
    country_code = (
        request.META.get("HTTP_CF_IPCOUNTRY", "")
        or request.META.get("HTTP_X_APPENGINE_COUNTRY", "")
    ).strip()[:8]
    city = request.META.get("HTTP_CF_IPCITY", "").strip()[:120]
    region = (
        request.META.get("HTTP_CF_REGION", "").strip()
        or request.META.get("HTTP_CF_REGION_CODE", "").strip()
    )[:120]
    postal_code = request.META.get("HTTP_CF_POSTAL_CODE", "").strip()[:32]
    latitude = _parse_coordinate(request.META.get("HTTP_CF_IPLATITUDE", ""))
    longitude = _parse_coordinate(request.META.get("HTTP_CF_IPLONGITUDE", ""))

    if (
        not city
        or not region
        or not postal_code
        or latitude is None
        or longitude is None
    ):
        ip = get_client_ip(request)
        if ip:
            fallback = _lookup_ip_geolocation(ip)
            country_code = _merge_geo_value(country_code, fallback["country_code"])
            city = _merge_geo_value(city, fallback["city"])
            region = _merge_geo_value(region, fallback["region"])
            postal_code = _merge_geo_value(postal_code, fallback["postal_code"])
            latitude = _merge_geo_value(latitude, fallback["latitude"])
            longitude = _merge_geo_value(longitude, fallback["longitude"])
            fallback_country_name = fallback.get("country_name", "")
        else:
            fallback_country_name = ""
    else:
        fallback_country_name = ""

    if country_code:
        country_name = COUNTRY_NAMES.get(country_code.upper(), country_code)
    else:
        country_name = fallback_country_name

    location_label = _build_location_label(
        city=city,
        region=region,
        postal_code=postal_code,
        country_name=country_name,
    )

    return {
        "country_code": country_code,
        "country_name": country_name[:100],
        "city": city,
        "region": region,
        "postal_code": postal_code,
        "latitude": latitude,
        "longitude": longitude,
        "location_label": location_label[:255],
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

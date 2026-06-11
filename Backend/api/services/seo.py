import os
from dataclasses import dataclass
from datetime import datetime
from xml.sax.saxutils import escape

from django.db.models import Q
from django.utils import timezone

from api.models import Campaign, ChefRecommendation
from api.services.frontend_access import is_frontend_public_access_enabled


@dataclass(frozen=True)
class SitemapEntry:
    path: str
    lastmod: datetime | None = None
    changefreq: str = "weekly"
    priority: str = "0.5"


def get_site_base_url(request) -> str:
    configured = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
    if configured:
        return configured

    scheme = "https" if request.is_secure() else "http"
    forwarded_proto = request.META.get("HTTP_X_FORWARDED_PROTO", "").split(",")[0].strip()
    if forwarded_proto in {"http", "https"}:
        scheme = forwarded_proto

    host = request.get_host().strip()
    return f"{scheme}://{host}"


def _format_lastmod(value: datetime | None) -> str:
    if value is None:
        return timezone.localdate().isoformat()
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value).date().isoformat()


def _active_campaigns():
    now = timezone.now()
    return (
        Campaign.objects.filter(is_active=True)
        .exclude(slug="")
        .filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        )
        .only("slug", "updated_at")
        .order_by("-priority", "pk")
    )


def _active_chef_recommendations():
    return (
        ChefRecommendation.objects.filter(status=ChefRecommendation.Status.ACTIVE)
        .exclude(slug="")
        .only("slug", "updated_at")
        .order_by("-pk")
    )


def build_sitemap_entries(*, public_access: bool) -> list[SitemapEntry]:
    if not public_access:
        return []

    entries: list[SitemapEntry] = [
        SitemapEntry(path="/", changefreq="daily", priority="1.0"),
        SitemapEntry(path="/menu", changefreq="daily", priority="0.9"),
        SitemapEntry(path="/about", changefreq="monthly", priority="0.7"),
        SitemapEntry(path="/adisyon", changefreq="weekly", priority="0.5"),
    ]

    for campaign in _active_campaigns():
        entries.append(
            SitemapEntry(
                path=f"/{campaign.slug}",
                lastmod=campaign.updated_at,
                changefreq="weekly",
                priority="0.8",
            )
        )

    for recommendation in _active_chef_recommendations():
        entries.append(
            SitemapEntry(
                path=f"/{recommendation.slug}",
                lastmod=recommendation.updated_at,
                changefreq="weekly",
                priority="0.8",
            )
        )

    return entries


def render_robots_txt(base_url: str, *, public_access: bool) -> str:
    sitemap_url = f"{base_url}/sitemap.xml"
    lines = ["User-agent: *"]

    if public_access:
        lines.extend(
            [
                "Allow: /",
                "Disallow: /login",
                "Disallow: /api/",
                "Disallow: /admin/",
            ]
        )
    else:
        lines.append("Disallow: /")

    lines.append("")
    lines.append(f"Sitemap: {sitemap_url}")
    return "\n".join(lines) + "\n"


def render_sitemap_xml(base_url: str, entries: list[SitemapEntry]) -> str:
    url_nodes: list[str] = []
    for entry in entries:
        loc = escape(f"{base_url}{entry.path}")
        lastmod = escape(_format_lastmod(entry.lastmod))
        changefreq = escape(entry.changefreq)
        priority = escape(entry.priority)
        url_nodes.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )

    body = "\n".join(url_nodes)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )

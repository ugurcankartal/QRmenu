from django.http import HttpResponse
from django.views.decorators.http import require_GET

from api.services.frontend_access import is_frontend_public_access_enabled
from api.services.seo import (
    build_sitemap_entries,
    get_site_base_url,
    render_robots_txt,
    render_sitemap_xml,
)


def _seo_cache_headers(response: HttpResponse) -> HttpResponse:
    response["Cache-Control"] = "public, max-age=3600"
    return response


@require_GET
def robots_txt_view(request):
    public_access = is_frontend_public_access_enabled()
    base_url = get_site_base_url(request)
    content = render_robots_txt(base_url, public_access=public_access)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    return _seo_cache_headers(response)


@require_GET
def sitemap_xml_view(request):
    public_access = is_frontend_public_access_enabled()
    base_url = get_site_base_url(request)
    entries = build_sitemap_entries(public_access=public_access)
    content = render_sitemap_xml(base_url, entries)
    response = HttpResponse(content, content_type="application/xml; charset=utf-8")
    return _seo_cache_headers(response)

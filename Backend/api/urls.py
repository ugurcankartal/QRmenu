from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth_views import (
    FrontendAccessStatusView,
    FrontendCsrfView,
    FrontendLoginView,
    FrontendMeView,
    FrontendTokenRefreshView,
)
from .seo_views import robots_txt_view, sitemap_xml_view
from .views import (
    CampaignViewSet,
    CategoryViewSet,
    ChefRecommendationViewSet,
    ProductViewSet,
    SiteSettingsView,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("campaigns", CampaignViewSet, basename="campaign")
router.register(
    "chef-recommendations",
    ChefRecommendationViewSet,
    basename="chef-recommendation",
)

urlpatterns = [
    path("robots.txt", robots_txt_view, name="api-robots-txt"),
    path("sitemap.xml", sitemap_xml_view, name="api-sitemap-xml"),
    path("access/status/", FrontendAccessStatusView.as_view(), name="frontend-access-status"),
    path("auth/csrf/", FrontendCsrfView.as_view(), name="frontend-auth-csrf"),
    path("auth/login/", FrontendLoginView.as_view(), name="frontend-auth-login"),
    path("auth/refresh/", FrontendTokenRefreshView.as_view(), name="frontend-auth-refresh"),
    path("auth/me/", FrontendMeView.as_view(), name="frontend-auth-me"),
    path("settings/", SiteSettingsView.as_view(), name="site-settings"),
    path("", include(router.urls)),
    path("", include("localization.api.urls")),
    path("", include("currency.api.urls")),
    path("", include("adisyon.api.urls")),
]

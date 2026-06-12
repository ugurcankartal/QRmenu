import re

from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from api.services.frontend_access import (
    is_frontend_public_access_enabled,
    user_can_view_frontend,
)

API_V1_PREFIX = "/api/v1/"
PUBLIC_API_PATHS = (
    "/api/v1/security/page-visit/",
    "/api/v1/robots.txt",
    "/api/v1/sitemap.xml",
    "/api/v1/access/status/",
    "/api/v1/auth/csrf/",
    "/api/v1/auth/login/",
    "/api/v1/auth/refresh/",
)


class FrontendAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._bearer_re = re.compile(r"^Bearer\s+(.+)$", re.IGNORECASE)

    def __call__(self, request):
        if not request.path.startswith(API_V1_PREFIX):
            return self.get_response(request)

        if any(request.path.startswith(path) for path in PUBLIC_API_PATHS):
            return self.get_response(request)

        if is_frontend_public_access_enabled():
            return self.get_response(request)

        authorization = request.META.get("HTTP_AUTHORIZATION", "")
        match = self._bearer_re.match(authorization)
        if not match:
            return JsonResponse(
                {"detail": "Ön yüz erişimi kapalı. Giriş yapmanız gerekiyor."},
                status=403,
            )

        try:
            token = AccessToken(match.group(1))
            user_id = token.get("user_id")
        except (InvalidToken, TokenError, KeyError):
            return JsonResponse({"detail": "Geçersiz veya süresi dolmuş oturum."}, status=401)

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.filter(pk=user_id, is_active=True).first()
        if not user or not user_can_view_frontend(user):
            return JsonResponse(
                {"detail": "Bu siteyi görüntüleme yetkiniz yok."},
                status=403,
            )

        request.user = user
        request.frontend_access_user = user
        return self.get_response(request)

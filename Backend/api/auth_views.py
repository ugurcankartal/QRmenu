from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from api.services.frontend_access import user_can_view_frontend

User = get_user_model()


class FrontendAccessStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from api.services.frontend_access import is_frontend_public_access_enabled

        return Response({"public_access": is_frontend_public_access_enabled()})


class FrontendCsrfView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class FrontendLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"detail": "Kullanıcı adı ve şifre gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Geçersiz kullanıcı adı veya şifre."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user_can_view_frontend(user):
            return Response(
                {"detail": "Yalnızca admin veya supervisor rolündeki kullanıcılar girebilir."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        groups = list(user.groups.order_by("name").values_list("name", flat=True))
        full_name = user.get_full_name().strip()

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.pk,
                    "username": user.get_username(),
                    "full_name": full_name,
                    "groups": groups,
                },
            }
        )


class FrontendMeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not user.is_authenticated or not user_can_view_frontend(user):
            return Response(
                {"detail": "Kimlik doğrulanamadı."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "id": user.pk,
                "username": user.get_username(),
                "full_name": user.get_full_name().strip(),
                "groups": list(user.groups.order_by("name").values_list("name", flat=True)),
            }
        )


class FrontendTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response

        try:
            refresh = RefreshToken(request.data.get("refresh"))
            user = User.objects.filter(pk=refresh.get("user_id"), is_active=True).first()
        except (InvalidToken, TokenError, KeyError):
            return Response(
                {"detail": "Geçersiz yenileme anahtarı."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user or not user_can_view_frontend(user):
            return Response(
                {"detail": "Bu siteyi görüntüleme yetkiniz yok."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return response

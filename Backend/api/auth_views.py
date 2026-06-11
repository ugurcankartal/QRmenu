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

from api.services.frontend_access import is_frontend_public_access_enabled, user_can_view_frontend
from security.models import FrontendLoginAudit
from security.services.client_fingerprint import get_client_ip
from security.services.login_audit import log_frontend_login_event
from security.services.login_rate_limit import (
    LOGIN_LOCKOUT_MINUTES,
    check_login_rate_limit,
    clear_login_rate_limit,
    record_failed_login_attempt,
)

User = get_user_model()


def _rate_limit_payload(status_obj):
    payload = {
        "remaining_attempts": status_obj.remaining_attempts,
    }
    if status_obj.retry_after_seconds:
        payload["retry_after_seconds"] = status_obj.retry_after_seconds
        payload["lockout_minutes"] = LOGIN_LOCKOUT_MINUTES
    if status_obj.locked_until:
        payload["locked_until"] = status_obj.locked_until.isoformat()
    return payload


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
        client_ip = get_client_ip(request)
        site_closed = not is_frontend_public_access_enabled()

        if site_closed:
            rate_status = check_login_rate_limit(client_ip)
            if not rate_status.allowed:
                log_frontend_login_event(
                    request,
                    event_type=FrontendLoginAudit.EventType.BLOCKED,
                    username_attempted=username,
                    failure_reason="Cok fazla basarisiz giris denemesi.",
                )
                return Response(
                    {
                        "detail": (
                            f"Cok fazla basarisiz deneme. "
                            f"{LOGIN_LOCKOUT_MINUTES} dakika bekleyin."
                        ),
                        **_rate_limit_payload(rate_status),
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        if not username or not password:
            log_frontend_login_event(
                request,
                event_type=FrontendLoginAudit.EventType.VALIDATION_ERROR,
                username_attempted=username,
                failure_reason="Kullanici adi veya sifre eksik.",
            )
            return Response(
                {"detail": "Kullanıcı adı ve şifre gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            rate_payload = {}
            if site_closed:
                fail_status = record_failed_login_attempt(client_ip)
                rate_payload = _rate_limit_payload(fail_status)
                if not fail_status.allowed:
                    log_frontend_login_event(
                        request,
                        event_type=FrontendLoginAudit.EventType.BLOCKED,
                        username_attempted=username,
                        failure_reason="Basarisiz deneme limiti asildi.",
                    )
                    return Response(
                        {
                            "detail": (
                                f"Cok fazla basarisiz deneme. "
                                f"{LOGIN_LOCKOUT_MINUTES} dakika bekleyin."
                            ),
                            **rate_payload,
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

            log_frontend_login_event(
                request,
                event_type=FrontendLoginAudit.EventType.FAILED,
                username_attempted=username,
                failure_reason="Gecersiz kullanici adi veya sifre.",
            )
            return Response(
                {
                    "detail": "Geçersiz kullanıcı adı veya şifre.",
                    **rate_payload,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user_can_view_frontend(user):
            if site_closed:
                record_failed_login_attempt(client_ip)
            log_frontend_login_event(
                request,
                event_type=FrontendLoginAudit.EventType.FORBIDDEN_ROLE,
                username_attempted=username,
                user=user,
                failure_reason="Yetkisiz rol.",
            )
            return Response(
                {"detail": "Yalnızca admin veya supervisor rolündeki kullanıcılar girebilir."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if site_closed:
            clear_login_rate_limit(client_ip)

        log_frontend_login_event(
            request,
            event_type=FrontendLoginAudit.EventType.SUCCESS,
            username_attempted=username,
            user=user,
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

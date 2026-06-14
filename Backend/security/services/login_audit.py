from security.models import FrontendLoginAudit
from security.services.client_fingerprint import build_client_fingerprint, pick_model_fields


def log_frontend_login_event(
    request,
    *,
    event_type: str,
    username_attempted: str = "",
    user=None,
    failure_reason: str = "",
) -> FrontendLoginAudit:
    fingerprint = pick_model_fields(
        FrontendLoginAudit,
        build_client_fingerprint(request),
    )
    security_headers = fingerprint.pop("security_headers", {})
    return FrontendLoginAudit.objects.create(
        event_type=event_type,
        user=user,
        username_attempted=username_attempted[:150],
        failure_reason=failure_reason[:255],
        security_headers=security_headers,
        **fingerprint,
    )

from security.models import FrontendLoginAudit
from security.services.client_fingerprint import build_client_fingerprint


def log_frontend_login_event(
    request,
    *,
    event_type: str,
    username_attempted: str = "",
    user=None,
    failure_reason: str = "",
) -> FrontendLoginAudit:
    fingerprint = build_client_fingerprint(request)
    return FrontendLoginAudit.objects.create(
        event_type=event_type,
        user=user,
        username_attempted=username_attempted[:150],
        failure_reason=failure_reason[:255],
        **fingerprint,
    )

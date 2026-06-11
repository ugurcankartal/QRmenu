from datetime import timedelta

from django.utils import timezone

from security.models import LoginAttemptState

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 5


class LoginRateLimitStatus:
    __slots__ = ("allowed", "remaining_attempts", "retry_after_seconds", "locked_until")

    def __init__(
        self,
        *,
        allowed: bool,
        remaining_attempts: int,
        retry_after_seconds: int = 0,
        locked_until=None,
    ):
        self.allowed = allowed
        self.remaining_attempts = remaining_attempts
        self.retry_after_seconds = retry_after_seconds
        self.locked_until = locked_until


def _lockout_duration():
    return timedelta(minutes=LOGIN_LOCKOUT_MINUTES)


def check_login_rate_limit(ip_address: str) -> LoginRateLimitStatus:
    if not ip_address:
        return LoginRateLimitStatus(
            allowed=True,
            remaining_attempts=MAX_FAILED_LOGIN_ATTEMPTS,
        )

    state = LoginAttemptState.objects.filter(ip_address=ip_address).first()
    if not state:
        return LoginRateLimitStatus(
            allowed=True,
            remaining_attempts=MAX_FAILED_LOGIN_ATTEMPTS,
        )

    now = timezone.now()
    if state.locked_until and state.locked_until > now:
        retry_after = int((state.locked_until - now).total_seconds())
        return LoginRateLimitStatus(
            allowed=False,
            remaining_attempts=0,
            retry_after_seconds=max(retry_after, 1),
            locked_until=state.locked_until,
        )

    if state.locked_until and state.locked_until <= now:
        state.failed_attempts = 0
        state.locked_until = None
        state.save(update_fields=["failed_attempts", "locked_until", "updated_at"])

    remaining = max(0, MAX_FAILED_LOGIN_ATTEMPTS - state.failed_attempts)
    return LoginRateLimitStatus(
        allowed=True,
        remaining_attempts=remaining or MAX_FAILED_LOGIN_ATTEMPTS,
    )


def record_failed_login_attempt(ip_address: str) -> LoginRateLimitStatus:
    if not ip_address:
        return LoginRateLimitStatus(
            allowed=True,
            remaining_attempts=MAX_FAILED_LOGIN_ATTEMPTS - 1,
        )

    now = timezone.now()
    state, _ = LoginAttemptState.objects.get_or_create(ip_address=ip_address)
    state.failed_attempts += 1

    if state.failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        state.locked_until = now + _lockout_duration()
        state.failed_attempts = 0
        state.save(update_fields=["failed_attempts", "locked_until", "updated_at"])
        retry_after = int(_lockout_duration().total_seconds())
        return LoginRateLimitStatus(
            allowed=False,
            remaining_attempts=0,
            retry_after_seconds=retry_after,
            locked_until=state.locked_until,
        )

    state.save(update_fields=["failed_attempts", "updated_at"])
    remaining = MAX_FAILED_LOGIN_ATTEMPTS - state.failed_attempts
    return LoginRateLimitStatus(
        allowed=True,
        remaining_attempts=remaining,
    )


def clear_login_rate_limit(ip_address: str) -> None:
    if ip_address:
        LoginAttemptState.objects.filter(ip_address=ip_address).delete()

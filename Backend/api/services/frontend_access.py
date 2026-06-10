from django.contrib.auth.models import Group

from api.models import SiteSettings

FRONTEND_ACCESS_GROUP_NAMES = frozenset({"admin", "supervisor"})


def get_active_site_settings():
    return (
        SiteSettings.objects.filter(is_active=True)
        .order_by("-updated_at", "pk")
        .first()
    )


def is_frontend_public_access_enabled() -> bool:
    settings = get_active_site_settings()
    if settings is None:
        return True
    return settings.frontend_public_access


def user_can_view_frontend(user) -> bool:
    if not user or not user.is_active:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__iexact="admin").exists() or user.groups.filter(
        name__iexact="supervisor"
    ).exists()


def ensure_frontend_access_groups():
    for name in sorted(FRONTEND_ACCESS_GROUP_NAMES):
        Group.objects.get_or_create(name=name)

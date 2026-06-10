def get_admin_site_name() -> str:
    try:
        from api.models import SiteSettings

        settings = (
            SiteSettings.objects.filter(is_active=True)
            .order_by("-updated_at", "pk")
            .first()
        )
        if settings and settings.name:
            return settings.name+" - Yönetim Paneli"
    except Exception:
        pass
    return "Django yönetimi"


def get_admin_user_display(user) -> str:
    if not user.is_authenticated:
        return ""

    group_names = list(user.groups.order_by("name").values_list("name", flat=True))
    full_name = user.get_full_name().strip()

    if group_names and full_name:
        return f"{', '.join(group_names)} — {full_name}"
    if full_name:
        return full_name
    if group_names:
        return ", ".join(group_names)
    return user.get_short_name() or user.get_username()

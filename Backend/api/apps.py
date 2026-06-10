from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "Api"

    def ready(self):
        from .admin_menu import patch_admin_site

        patch_admin_site()

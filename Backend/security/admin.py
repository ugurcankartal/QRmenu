from django.contrib import admin

from security.models import FrontendLoginAudit, LoginAttemptState, SqlInjectionAttempt


@admin.register(FrontendLoginAudit)
class FrontendLoginAuditAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "event_type",
        "username_attempted",
        "ip_address",
        "location_label",
        "device_type",
        "browser_name",
        "is_mobile",
    )
    list_filter = ("event_type", "device_type", "is_mobile", "is_bot", "country_code")
    search_fields = (
        "username_attempted",
        "ip_address",
        "user_agent",
        "city",
        "country_name",
        "failure_reason",
    )
    readonly_fields = [field.name for field in FrontendLoginAudit._meta.fields]
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SqlInjectionAttempt)
class SqlInjectionAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "ip_address",
        "location_label",
        "request_method",
        "request_path",
        "matched_pattern",
        "device_type",
        "browser_name",
    )
    list_filter = ("request_method", "country_code", "device_type", "is_bot")
    search_fields = (
        "ip_address",
        "matched_pattern",
        "matched_value",
        "request_path",
        "user_agent",
        "query_string",
    )
    readonly_fields = [field.name for field in SqlInjectionAttempt._meta.fields]
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginAttemptState)
class LoginAttemptStateAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "failed_attempts", "locked_until", "updated_at")
    search_fields = ("ip_address",)
    readonly_fields = ("updated_at",)
    ordering = ("-updated_at",)

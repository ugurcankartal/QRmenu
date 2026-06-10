from django.contrib import admin
from django.utils.html import format_html

from localization.admin_mixins import GroqTranslateAdminMixin
from localization.models import Language, UiString, UiStringKey


class UiStringInline(admin.TabularInline):
    model = UiString
    extra = 0
    raw_id_fields = ("language",)


@admin.register(UiStringKey)
class UiStringKeyAdmin(admin.ModelAdmin):
    search_fields = ("key", "help_text")
    list_display = ("key", "help_text")
    inlines = [UiStringInline]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "flag_preview",
        "code",
        "name_native",
        "is_active",
        "is_default",
        "sort_order",
    )
    list_display_links = ("code", "name_native")
    list_editable = ("is_active",)
    list_filter = ("is_active", "is_default")
    readonly_fields = ("flag_preview",)
    fields = (
        "code",
        "name_native",
        "flag",
        "flag_preview",
        "is_active",
        "is_default",
        "sort_order",
    )

    @admin.display(description="Bayrak")
    def flag_preview(self, obj):
        if obj.flag:
            return format_html(
                '<img src="{}" alt="" style="height:32px;width:auto;border-radius:4px;" />',
                obj.flag.url,
            )
        return "—"


@admin.register(UiString)
class UiStringAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "ui_string"
    list_display = ("language", "key", "text")
    list_filter = ("language",)
    search_fields = ("text", "key__key")
    raw_id_fields = ("key",)

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from localization.services.groq_translation import get_default_language
from localization.services.groq_translation_runner import (
    get_groq_translation_status,
    is_groq_translation_running,
    start_groq_translation_background,
)


class GroqTranslateAdminMixin:
    change_list_template = "admin/groq_translate_change_list.html"
    groq_translation_handler: str | None = None

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path(
                "groq-translate/",
                self.admin_site.admin_view(self.groq_translate_view),
                name="%s_%s_groq_translate" % info,
            ),
        ]
        return custom_urls + super().get_urls()

    def groq_translate_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        if request.method != "POST":
            return HttpResponseRedirect(self._groq_changelist_url())

        handler_name = self.groq_translation_handler
        if not handler_name:
            messages.error(request, "Bu model için Groq çeviri işleyicisi tanımlı değil.")
            return HttpResponseRedirect(self._groq_changelist_url())

        outcome = start_groq_translation_background(handler_name)
        if outcome == "already_running":
            messages.warning(
                request,
                "Groq çevirisi zaten arka planda çalışıyor. Birkaç dakika sonra sayfayı yenileyin.",
            )
        elif outcome == "spawn_error":
            messages.error(
                request,
                "Groq çevirisi başlatılamadı. Sunucu loglarını kontrol edin.",
            )
        else:
            messages.success(
                request,
                (
                    "Groq çevirisi arka planda başlatıldı. "
                    "Cloudflare zaman aşımı olmadan tamamlanacak; "
                    "birkaç dakika sonra bu sayfayı yenileyin."
                ),
            )

        return HttpResponseRedirect(self._groq_changelist_url())

    def _groq_changelist_url(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return reverse("admin:%s_%s_changelist" % info)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        info = self.model._meta.app_label, self.model._meta.model_name
        handler_name = self.groq_translation_handler
        default_language = get_default_language()
        extra_context["groq_translate_url"] = reverse(
            "admin:%s_%s_groq_translate" % info
        )
        extra_context["default_language"] = default_language
        extra_context["groq_translation_running"] = (
            is_groq_translation_running(handler_name) if handler_name else False
        )
        extra_context["groq_translation_status"] = (
            get_groq_translation_status(handler_name) if handler_name else None
        )
        return super().changelist_view(request, extra_context)

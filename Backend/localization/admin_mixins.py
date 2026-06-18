from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse

from localization.services.groq_translation import get_default_language
from localization.services.groq_translation_progress import get_groq_translation_progress
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
            path(
                "groq-translate/status/",
                self.admin_site.admin_view(self.groq_translate_status_view),
                name="%s_%s_groq_translate_status" % info,
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
            messages.warning(request, "Groq çevirisi zaten çalışıyor.")
        elif outcome == "spawn_error":
            messages.error(
                request,
                "Groq çevirisi başlatılamadı. Sunucu loglarını kontrol edin.",
            )
        else:
            messages.success(
                request,
                "Groq çevirisi başlatıldı. İlerleme çubuğundan takip edebilirsiniz.",
            )

        return HttpResponseRedirect(self._groq_changelist_url())

    def groq_translate_status_view(self, request):
        if not self.has_view_permission(request):
            raise PermissionDenied

        handler_name = self.groq_translation_handler
        if not handler_name:
            return JsonResponse({"status": "idle"})

        progress = get_groq_translation_progress(handler_name)
        if progress:
            return JsonResponse(progress)

        if is_groq_translation_running(handler_name):
            return JsonResponse(
                {
                    "status": "running",
                    "total": 0,
                    "current": 0,
                    "percent": 0,
                    "label": "Baslatiliyor…",
                    "errors": [],
                }
            )

        result = get_groq_translation_status(handler_name)
        if result:
            return JsonResponse(
                {
                    "status": "error" if result.get("error") else "done",
                    "percent": 100,
                    "label": result.get("error") or "Tamamlandi.",
                    "errors": [result["error"]] if result.get("error") else [],
                    "stats": result.get("stats"),
                }
            )

        return JsonResponse({"status": "idle"})

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
        extra_context["groq_translate_status_url"] = reverse(
            "admin:%s_%s_groq_translate_status" % info
        )
        extra_context["default_language"] = default_language
        extra_context["groq_translation_running"] = (
            is_groq_translation_running(handler_name) if handler_name else False
        )
        extra_context["groq_translation_progress"] = (
            get_groq_translation_progress(handler_name) if handler_name else None
        )
        extra_context["groq_translation_status"] = (
            get_groq_translation_status(handler_name) if handler_name else None
        )
        return super().changelist_view(request, extra_context)

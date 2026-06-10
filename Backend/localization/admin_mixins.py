from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse
from django.views.decorators.http import require_POST

from core.groq_client import GroqAPIError
from localization.services.groq_translation import get_default_language, run_groq_translation


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

        try:
            stats = run_groq_translation(handler_name)
        except GroqAPIError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            messages.error(request, f"Çeviri sırasında hata oluştu: {exc}")
        else:
            created = stats.get("created", 0)
            skipped = stats.get("skipped", 0)
            languages = stats.get("languages", 0)
            if created == 0 and skipped > 0:
                messages.info(
                    request,
                    f"Tüm çeviriler zaten mevcut ({skipped} kayıt atlandı).",
                )
            elif created == 0:
                messages.info(request, "Çevrilecek yeni kayıt bulunamadı.")
            else:
                messages.success(
                    request,
                    (
                        f"Groq çevirisi tamamlandı: {created} yeni kayıt "
                        f"({languages} dil), {skipped} mevcut çeviri atlandı."
                    ),
                )

        return HttpResponseRedirect(self._groq_changelist_url())

    def _groq_changelist_url(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return reverse("admin:%s_%s_changelist" % info)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        info = self.model._meta.app_label, self.model._meta.model_name
        default_language = get_default_language()
        extra_context["groq_translate_url"] = reverse(
            "admin:%s_%s_groq_translate" % info
        )
        extra_context["default_language"] = default_language
        return super().changelist_view(request, extra_context)

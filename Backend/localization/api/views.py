from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from localization.api.serializers import LanguageSerializer
from localization.models import Language
from localization.services.i18n_bundle import default_i18n_bundle_provider


def _lang_from_request(request) -> str | None:
    lang = request.query_params.get("lang")
    if lang:
        return lang.strip().split(";")[0].strip()
    accept = request.headers.get("Accept-Language")
    if accept:
        first = accept.split(",")[0].strip()
        return first.split(";")[0].strip()
    return None


class LanguageListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Language.objects.filter(is_active=True).order_by("sort_order", "code")
        return Response(
            LanguageSerializer(qs, many=True, context={"request": request}).data
        )


class I18nBundleView(APIView):
    """Flat JSON map of UI keys for React / React Native clients."""

    permission_classes = [AllowAny]

    def get(self, request):
        lang = _lang_from_request(request)
        resolved, bundle = default_i18n_bundle_provider.build_bundle(lang)
        return Response({"language": resolved, "strings": bundle})

from django.urls import path

from localization.api.views import I18nBundleView, LanguageListView

urlpatterns = [
    path("languages/", LanguageListView.as_view(), name="i18n-languages"),
    path("bundle/", I18nBundleView.as_view(), name="i18n-bundle"),
]

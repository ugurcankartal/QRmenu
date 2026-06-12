from django.urls import path

from security.views import PageVisitLogView

urlpatterns = [
    path("page-visit/", PageVisitLogView.as_view(), name="security-page-visit"),
]

from django.urls import path

from adisyon.api.views import (
    AdisyonItemDetailView,
    AdisyonToggleProductView,
    AdisyonView,
)

urlpatterns = [
    path("adisyon/", AdisyonView.as_view(), name="adisyon-detail"),
    path(
        "adisyon/toggle/",
        AdisyonToggleProductView.as_view(),
        name="adisyon-toggle",
    ),
    path(
        "adisyon/items/<int:item_id>/",
        AdisyonItemDetailView.as_view(),
        name="adisyon-item-detail",
    ),
]

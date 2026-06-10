from django.urls import path

from currency.api.views import CurrencyListView

urlpatterns = [
    path("currencies/", CurrencyListView.as_view(), name="currency-list"),
]

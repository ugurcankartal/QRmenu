from rest_framework import generics

from currency.api.serializers import CurrencySerializer
from currency.models import Currency


class CurrencyListView(generics.ListAPIView):
    queryset = Currency.objects.filter(is_active=True).order_by("order", "code")
    serializer_class = CurrencySerializer

from decimal import Decimal

from rest_framework import serializers

from adisyon.money import truncate_money


def decimal_to_plain_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return format(truncate_money(value), "f")


class PlainDecimalField(serializers.Field):
    """Ondalık değeri yuvarlamadan düz metin olarak döner."""

    def to_representation(self, value):
        if value is None:
            return None
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return decimal_to_plain_str(value)

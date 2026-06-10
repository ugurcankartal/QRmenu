from decimal import ROUND_DOWN, Decimal

TWOPLACES = Decimal("0.01")


def truncate_money(value: Decimal) -> Decimal:
    """2 ondalık basamağa keser (yuvarlamaz)."""
    return value.quantize(TWOPLACES, rounding=ROUND_DOWN)

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from adisyon.campaign_pricing import (
    calculate_discounted_line_total,
    effective_discounted_unit_price,
    find_best_campaign_rule,
)
from adisyon.money import truncate_money
from adisyon.models import Adisyon, AdisyonItem, SessionKey, SessionKeyPolicy


def get_product_pricing(product):
    """Ürünün güncel fiyat ve para birimini döner."""
    from currency.models import Currency

    price = product.price
    product_currency = getattr(product, "product_currency", None)
    if product_currency:
        currency = product_currency.currency
    else:
        currency = Currency.objects.filter(code="TRY", is_active=True).first()
    return price, currency


def apply_item_pricing(item: AdisyonItem, product=None, *, is_new: bool = False) -> None:
    """Satır fiyat anlık görüntüsünü günceller; birim fiyat yalnızca yeni kayıtta sabitlenir."""
    source_product = product or item.product

    if is_new:
        price, currency = get_product_pricing(source_product)
        item.price = truncate_money(price)
        item.currency = currency

    item.campaign_rule = find_best_campaign_rule(
        source_product,
        item.quantity,
        item.price or Decimal("0.00"),
    )

    line_total = truncate_money((item.price or Decimal("0")) * item.quantity)
    item.amount = line_total
    item.total_price = line_total

    if item.campaign_rule_id:
        item.discounted_price = effective_discounted_unit_price(
            item.price,
            item.quantity,
            item.campaign_rule,
        )
    else:
        item.discounted_price = item.price


def recalculate_adisyon(adisyon: Adisyon) -> None:
    """Adisyon toplamını kalemlerin saklanan satır tutarlarından hesaplar."""
    items = list(
        adisyon.items.select_related("currency", "campaign_rule").order_by(
            "order",
            "created_at",
        ),
    )
    total = Decimal("0.00")
    discounted_total = Decimal("0.00")

    for item in items:
        line_total = item.total_price or Decimal("0.00")
        total += line_total

        if item.campaign_rule_id:
            discounted_total += calculate_discounted_line_total(
                item.price,
                item.quantity,
                item.campaign_rule,
            )
        else:
            discounted_total += line_total

    adisyon.total_price = truncate_money(total)
    adisyon.discounted_total_price = truncate_money(discounted_total)
    adisyon.currency = items[0].currency if items else None
    adisyon.save(
        update_fields=[
            "total_price",
            "discounted_total_price",
            "currency",
            "updated_at",
        ],
    )


def get_refresh_duration_minutes() -> int:
    return SessionKeyPolicy.get_solo().refresh_duration_minutes


def create_session_key() -> SessionKey:
    duration_minutes = get_refresh_duration_minutes()
    now = timezone.now()
    session_key = SessionKey.objects.create(
        key=SessionKey.generate_key(),
        refresh_duration_minutes=duration_minutes,
        last_activity_at=now,
        expires_at=now + timedelta(minutes=duration_minutes),
    )
    Adisyon.objects.create(session_key=session_key)
    return session_key


def refresh_session(session_key: SessionKey) -> SessionKey:
    now = timezone.now()
    session_key.last_activity_at = now
    session_key.expires_at = now + timedelta(minutes=session_key.refresh_duration_minutes)
    session_key.save(
        update_fields=["last_activity_at", "expires_at", "updated_at"],
    )
    return session_key


def resolve_session(raw_key: str | None) -> tuple[SessionKey, bool]:
    """Oturumu çöz; (session_key, created) döner."""
    if raw_key:
        session_key = (
            SessionKey.objects.select_related("adisyon")
            .filter(key=raw_key)
            .first()
        )
        if session_key and not session_key.is_expired:
            refresh_session(session_key)
            return session_key, False

    return create_session_key(), True

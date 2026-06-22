from rest_framework import serializers

from adisyon.api.fields import PlainDecimalField, decimal_to_plain_str
from adisyon.models import Adisyon, AdisyonItem
from adisyon.querysets import active_adisyon_items_queryset
from adisyon.services import compute_adisyon_totals_from_items
from api.serializers import ProductSerializer


def _active_items_for_adisyon(adisyon: Adisyon) -> list[AdisyonItem]:
    prefetched = getattr(adisyon, "_prefetched_objects_cache", {})
    if "items" in prefetched:
        return list(adisyon.items.all())

    return list(
        active_adisyon_items_queryset()
        .filter(adisyon=adisyon)
        .select_related("currency", "campaign_rule")
        .order_by("order", "created_at")
    )


class AdisyonItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    currency_symbol = serializers.CharField(source="currency.symbol", read_only=True)
    price = PlainDecimalField(read_only=True)
    discounted_price = PlainDecimalField(read_only=True)
    campaign_badge = serializers.SerializerMethodField()

    class Meta:
        model = AdisyonItem
        fields = [
            "id",
            "product",
            "quantity",
            "order",
            "price",
            "discounted_price",
            "campaign_rule",
            "campaign_badge",
            "currency",
            "currency_code",
            "currency_symbol",
            "amount",
            "total_price",
        ]
        read_only_fields = [
            "id",
            "product",
            "price",
            "discounted_price",
            "campaign_rule",
            "campaign_badge",
            "currency",
            "currency_code",
            "currency_symbol",
            "amount",
            "total_price",
        ]

    def get_campaign_badge(self, obj):
        if not obj.campaign_rule_id:
            return ""

        campaign = obj.campaign_rule.campaign
        translation = campaign.get_translation(self.context.get("language_code"))
        return translation.badge if translation else ""


class AdisyonSerializer(serializers.ModelSerializer):
    items = AdisyonItemSerializer(many=True, read_only=True)
    total_price = PlainDecimalField(read_only=True)
    discounted_total_price = PlainDecimalField(read_only=True)
    session_key = serializers.CharField(source="session_key.key", read_only=True)
    expires_at = serializers.SerializerMethodField()
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    currency_symbol = serializers.CharField(source="currency.symbol", read_only=True)
    product_ids = serializers.SerializerMethodField()

    class Meta:
        model = Adisyon
        fields = [
            "id",
            "session_key",
            "expires_at",
            "items",
            "product_ids",
            "total_price",
            "discounted_total_price",
            "currency",
            "currency_code",
            "currency_symbol",
            "updated_at",
        ]

    def get_expires_at(self, obj):
        return obj.session_key.policy_expires_at

    def get_product_ids(self, obj):
        return [item.product_id for item in _active_items_for_adisyon(obj)]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        items = _active_items_for_adisyon(instance)
        total, discounted_total, currency = compute_adisyon_totals_from_items(items)

        data["total_price"] = decimal_to_plain_str(total)
        data["discounted_total_price"] = decimal_to_plain_str(discounted_total)
        if currency:
            data["currency"] = currency.pk
            data["currency_code"] = currency.code
            data["currency_symbol"] = currency.symbol
        else:
            data["currency"] = None
            data["currency_code"] = None
            data["currency_symbol"] = None

        return data

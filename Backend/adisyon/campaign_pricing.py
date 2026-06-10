from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from adisyon.money import truncate_money


def get_active_campaigns_for_product(product):
    from api.models import Campaign

    now = timezone.now()
    return (
        Campaign.objects.filter(is_active=True, products=product)
        .filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        )
        .prefetch_related("rules")
        .order_by("-priority", "pk")
    )


def rule_applies(rule, quantity: int) -> bool:
    from api.models import CampaignRule

    if rule.rule_type in (
        CampaignRule.RuleType.PERCENTAGE,
        CampaignRule.RuleType.FIXED_AMOUNT,
        CampaignRule.RuleType.BUY_X_GET_Y,
    ):
        return quantity >= 1

    if rule.rule_type == CampaignRule.RuleType.NTH_ITEM:
        return quantity >= (rule.item_ordinal or 0)

    return False


def find_best_campaign_rule(product, quantity: int, price: Decimal):
    """Tüm uygulanabilir kurallar arasından en düşük satır tutarını vereni seçer."""
    regular_total = price * quantity
    best_rule = None
    best_total = None

    for campaign in get_active_campaigns_for_product(product):
        for rule in campaign.rules.all().order_by("order", "pk"):
            if not rule_applies(rule, quantity):
                continue

            line_total = calculate_discounted_line_total(price, quantity, rule)
            if line_total >= regular_total:
                continue

            if best_total is None or line_total < best_total:
                best_total = line_total
                best_rule = rule

    return best_rule


def calculate_discounted_line_total(
    price: Decimal,
    quantity: int,
    rule,
) -> Decimal:
    from api.models import CampaignRule

    if quantity < 1:
        return truncate_money(Decimal("0"))

    if rule.rule_type == CampaignRule.RuleType.PERCENTAGE:
        multiplier = Decimal("1") - (rule.discount_percent / Decimal("100"))
        return truncate_money(price * multiplier * quantity)

    if rule.rule_type == CampaignRule.RuleType.FIXED_AMOUNT:
        unit = max(Decimal("0"), price - rule.discount_amount)
        return truncate_money(unit * quantity)

    if rule.rule_type == CampaignRule.RuleType.BUY_X_GET_Y:
        buy = rule.buy_quantity
        reward = rule.reward_quantity
        bundle = buy + reward
        discount_mult = (Decimal("100") - rule.discount_percent) / Decimal("100")

        full_bundles = quantity // bundle
        remainder = quantity % bundle

        total = Decimal(full_bundles) * Decimal(buy) * price
        total += Decimal(min(remainder, buy)) * price
        if remainder > buy:
            total += Decimal(remainder - buy) * price * discount_mult
        return truncate_money(total)

    if rule.rule_type == CampaignRule.RuleType.NTH_ITEM:
        n = rule.item_ordinal
        discount_mult = (Decimal("100") - rule.discount_percent) / Decimal("100")
        total = Decimal("0")
        for index in range(1, quantity + 1):
            if index % n == 0:
                total += price * discount_mult
            else:
                total += price
        return truncate_money(total)

    return truncate_money(price * quantity)


def effective_discounted_unit_price(
    price: Decimal,
    quantity: int,
    rule,
) -> Decimal:
    line_total = calculate_discounted_line_total(price, quantity, rule)
    if quantity < 1:
        return truncate_money(Decimal("0"))
    return truncate_money(line_total / quantity)

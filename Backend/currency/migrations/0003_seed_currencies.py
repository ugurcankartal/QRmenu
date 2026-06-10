from django.db import migrations


def seed_currencies(apps, schema_editor):
    Currency = apps.get_model("currency", "Currency")
    CurrencyExchangeRate = apps.get_model("currency", "CurrencyExchangeRate")

    try_currency, _ = Currency.objects.get_or_create(
        code="TRY",
        defaults={
            "name": "Turkish Lira",
            "symbol": "₺",
            "is_active": True,
            "order": 1,
        },
    )
    usd_currency, _ = Currency.objects.get_or_create(
        code="USD",
        defaults={
            "name": "US Dollar",
            "symbol": "$",
            "is_active": True,
            "order": 2,
        },
    )
    eur_currency, _ = Currency.objects.get_or_create(
        code="EUR",
        defaults={
            "name": "Euro",
            "symbol": "€",
            "is_active": True,
            "order": 3,
        },
    )

    pairs = [
        (try_currency, usd_currency, "0.031000", "0.032000"),
        (try_currency, eur_currency, "0.028500", "0.029500"),
        (usd_currency, try_currency, "31.250000", "32.250000"),
        (eur_currency, try_currency, "33.900000", "35.100000"),
    ]
    for from_currency, to_currency, buy_rate, sell_rate in pairs:
        CurrencyExchangeRate.objects.get_or_create(
            from_currency=from_currency,
            to_currency=to_currency,
            defaults={
                "buy_rate": buy_rate,
                "sell_rate": sell_rate,
                "is_active": True,
            },
        )


def unseed_currencies(apps, schema_editor):
    Currency = apps.get_model("currency", "Currency")
    Currency.objects.filter(code__in=["TRY", "USD", "EUR"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("currency", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_currencies, unseed_currencies),
    ]

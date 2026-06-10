from decimal import Decimal

from django.db import migrations


def backfill_price_snapshots(apps, schema_editor):
    Adisyon = apps.get_model("adisyon", "Adisyon")
    AdisyonItem = apps.get_model("adisyon", "AdisyonItem")
    ProductCurrency = apps.get_model("currency", "ProductCurrency")
    Currency = apps.get_model("currency", "Currency")

    default_currency = Currency.objects.filter(code="TRY", is_active=True).first()

    for item in AdisyonItem.objects.select_related("product").iterator():
        product = item.product
        item.price = product.price

        product_currency = (
            ProductCurrency.objects.filter(product_id=product.id)
            .select_related("currency")
            .first()
        )
        item.currency = (
            product_currency.currency if product_currency else default_currency
        )

        line_total = (item.price or Decimal("0.00")) * item.quantity
        item.amount = line_total
        item.total_price = line_total
        item.save(
            update_fields=[
                "price",
                "currency",
                "amount",
                "total_price",
                "updated_at",
            ],
        )

    for adisyon in Adisyon.objects.iterator():
        items = list(
            AdisyonItem.objects.filter(adisyon_id=adisyon.id)
            .select_related("currency")
            .order_by("order", "created_at"),
        )
        total = sum((item.total_price or Decimal("0.00")) for item in items)
        adisyon.total_price = total
        adisyon.currency = items[0].currency if items else None
        adisyon.save(update_fields=["total_price", "currency", "updated_at"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("adisyon", "0003_price_snapshots"),
        ("currency", "0003_seed_currencies"),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_price_snapshots, noop),
    ]

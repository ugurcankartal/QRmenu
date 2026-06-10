from decimal import Decimal

from django.db import migrations, models


def recalculate_with_truncate(apps, schema_editor):
    from adisyon.models import Adisyon, AdisyonItem
    from adisyon.services import apply_item_pricing, recalculate_adisyon

    adisyon_ids = set()
    for item in AdisyonItem.objects.select_related("product").iterator():
        apply_item_pricing(item, is_new=False)
        item.save()
        adisyon_ids.add(item.adisyon_id)

    for adisyon_id in adisyon_ids:
        recalculate_adisyon(Adisyon.objects.get(pk=adisyon_id))


class Migration(migrations.Migration):

    dependencies = [
        ("adisyon", "0008_decimal_precision_no_round"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adisyon",
            name="discounted_total_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="İndirimli toplam tutar",
            ),
        ),
        migrations.AlterField(
            model_name="adisyon",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                verbose_name="Toplam tutar",
            ),
        ),
        migrations.AlterField(
            model_name="adisyonitem",
            name="discounted_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Kampanya kuralı uygulandığında birim fiyat (ortalama).",
                max_digits=10,
                verbose_name="İndirimli birim fiyat",
            ),
        ),
        migrations.AlterField(
            model_name="adisyonitem",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Ürün adisyona eklendiği andaki birim fiyat.",
                max_digits=10,
                verbose_name="Birim fiyat",
            ),
        ),
        migrations.RunPython(recalculate_with_truncate, migrations.RunPython.noop),
    ]

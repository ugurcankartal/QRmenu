from django.db import migrations


def backfill_discounted_prices(apps, schema_editor):
    Adisyon = apps.get_model("adisyon", "Adisyon")
    AdisyonItem = apps.get_model("adisyon", "AdisyonItem")

    for item in AdisyonItem.objects.iterator():
        item.discounted_price = item.price
        item.save(update_fields=["discounted_price", "updated_at"])

    for adisyon in Adisyon.objects.iterator():
        adisyon.discounted_total_price = adisyon.total_price
        adisyon.save(update_fields=["discounted_total_price", "updated_at"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("adisyon", "0005_discounted_prices"),
    ]

    operations = [
        migrations.RunPython(backfill_discounted_prices, noop),
    ]

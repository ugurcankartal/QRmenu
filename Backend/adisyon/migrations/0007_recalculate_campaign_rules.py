from django.db import migrations


def recalculate_campaign_rules(apps, schema_editor):
    from adisyon.models import Adisyon, AdisyonItem
    from adisyon.services import apply_item_pricing, recalculate_adisyon

    adisyon_ids = set()
    for item in AdisyonItem.objects.select_related("product").iterator():
        apply_item_pricing(item, is_new=False)
        item.save()
        adisyon_ids.add(item.adisyon_id)

    for adisyon_id in adisyon_ids:
        recalculate_adisyon(Adisyon.objects.get(pk=adisyon_id))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("adisyon", "0006_backfill_discounted_prices"),
    ]

    operations = [
        migrations.RunPython(recalculate_campaign_rules, noop),
    ]

from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model("api", "Category")
    categories = [
        ("Kebabs", "kebabs", 1),
        ("Grills", "grills", 2),
        ("Pides", "pides", 3),
        ("Appetizers", "appetizers", 4),
        ("Desserts", "desserts", 5),
        ("Beverages", "beverages", 6),
    ]
    for name, slug, order in categories:
        Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "order": order},
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("api", "Category")
    Category.objects.filter(
        slug__in=["kebabs", "grills", "pides", "appetizers", "desserts", "beverages"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]

import json

from django.db import migrations, models


def _parse_tag_text(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [
        part.strip()
        for part in text.replace("\n", ",").replace(";", ",").split(",")
        if part.strip()
    ]


_captured_translation_tags = {}


def capture_translation_tags(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT id, ingredients, allergens FROM api_producttranslation")
        for row_id, ingredients, allergens in cursor.fetchall():
            _captured_translation_tags[row_id] = (
                _parse_tag_text(ingredients),
                _parse_tag_text(allergens),
            )


def normalize_empty_text_to_json_array(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT id FROM api_producttranslation")
        row_ids = [row[0] for row in cursor.fetchall()]
        for row_id in row_ids:
            ingredients, allergens = _captured_translation_tags.get(row_id, ([], []))
            cursor.execute(
                """
                UPDATE api_producttranslation
                SET ingredients = %s, allergens = %s
                WHERE id = %s
                """,
                [
                    json.dumps(ingredients, ensure_ascii=False),
                    json.dumps(allergens, ensure_ascii=False),
                    row_id,
                ],
            )


def apply_translation_tags(apps, schema_editor):
    ProductTranslation = apps.get_model("api", "ProductTranslation")
    for translation in ProductTranslation.objects.all():
        ingredients, allergens = _captured_translation_tags.get(
            translation.pk,
            ([], []),
        )
        translation.ingredients = ingredients
        translation.allergens = allergens
        translation.save(update_fields=["ingredients", "allergens"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_product_producttranslation"),
    ]

    operations = [
        migrations.RunPython(capture_translation_tags, migrations.RunPython.noop),
        migrations.RunPython(
            normalize_empty_text_to_json_array,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="producttranslation",
            name="allergens",
            field=models.JSONField(blank=True, default=list, verbose_name="Alerjenler"),
        ),
        migrations.AlterField(
            model_name="producttranslation",
            name="ingredients",
            field=models.JSONField(blank=True, default=list, verbose_name="İçindekiler"),
        ),
        migrations.RunPython(apply_translation_tags, migrations.RunPython.noop),
    ]

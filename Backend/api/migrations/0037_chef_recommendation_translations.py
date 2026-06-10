import django.db.models.deletion
from django.db import migrations, models


def migrate_chef_recommendation_texts(apps, schema_editor):
    ChefRecommendation = apps.get_model("api", "ChefRecommendation")
    ChefRecommendationTranslation = apps.get_model("api", "ChefRecommendationTranslation")
    Language = apps.get_model("localization", "Language")

    default_language = (
        Language.objects.filter(is_active=True, is_default=True).first()
        or Language.objects.filter(is_active=True).order_by("sort_order", "code").first()
    )
    if not default_language:
        return

    for recommendation in ChefRecommendation.objects.all():
        title = recommendation.title or ""
        description = recommendation.description or ""
        if not title and not description:
            continue
        ChefRecommendationTranslation.objects.update_or_create(
            chef_recommendation_id=recommendation.pk,
            language_id=default_language.pk,
            defaults={
                "title": title or f"Şefin önerisi #{recommendation.pk}",
                "description": description,
            },
        )


def unmigrate_chef_recommendation_texts(apps, schema_editor):
    ChefRecommendation = apps.get_model("api", "ChefRecommendation")
    ChefRecommendationTranslation = apps.get_model("api", "ChefRecommendationTranslation")

    for recommendation in ChefRecommendation.objects.all():
        translation = (
            ChefRecommendationTranslation.objects.filter(
                chef_recommendation_id=recommendation.pk,
            )
            .order_by("pk")
            .first()
        )
        if translation:
            recommendation.title = translation.title
            recommendation.description = translation.description
            recommendation.save(update_fields=["title", "description"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0036_chef_recommendation_product_order"),
        ("localization", "0002_seed_languages"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChefRecommendationTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=150, verbose_name="Başlık")),
                ("description", models.TextField(blank=True, verbose_name="Açıklama")),
                (
                    "chef_recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="api.chefrecommendation",
                        verbose_name="Şefin önerisi",
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chef_recommendation_translations",
                        to="localization.language",
                        verbose_name="Dil",
                    ),
                ),
            ],
            options={
                "verbose_name": "Şefin önerisi çevirisi",
                "verbose_name_plural": "Şefin önerisi çevirileri",
            },
        ),
        migrations.AddConstraint(
            model_name="chefrecommendationtranslation",
            constraint=models.UniqueConstraint(
                fields=("chef_recommendation", "language"),
                name="unique_chef_recommendation_translation_per_language",
            ),
        ),
        migrations.RunPython(
            migrate_chef_recommendation_texts,
            unmigrate_chef_recommendation_texts,
        ),
        migrations.RemoveField(
            model_name="chefrecommendation",
            name="title",
        ),
        migrations.RemoveField(
            model_name="chefrecommendation",
            name="description",
        ),
    ]

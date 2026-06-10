from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0030_contact_translations"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="icon",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Otomatik (türe göre)"),
                    ("Phone", "Telefon"),
                    ("Printer", "Faks"),
                    ("Mail", "E-posta"),
                    ("MapPin", "Konum"),
                    ("Instagram", "Instagram"),
                    ("Facebook", "Facebook"),
                    ("Twitter", "X (Twitter)"),
                    ("MessageCircle", "WhatsApp"),
                    ("Youtube", "Youtube"),
                    ("Linkedin", "Linkedin"),
                    ("Music", "TikTok"),
                    ("Globe", "Web sitesi"),
                    ("Link", "Diğer"),
                ],
                help_text="Boş bırakılırsa türe göre otomatik seçilir.",
                max_length=30,
                verbose_name="İkon",
            ),
        ),
        migrations.AddField(
            model_name="contacttranslation",
            name="link_text",
            field=models.CharField(
                blank=True,
                help_text="URL için bağlantı metni (örn: @alt_fila). Boş bırakılırsa değer gösterilir.",
                max_length=150,
                verbose_name="Görünen ad",
            ),
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0046_security_audit_models"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="FrontendLoginAudit"),
                migrations.DeleteModel(name="SqlInjectionAttempt"),
                migrations.DeleteModel(name="LoginAttemptState"),
            ],
        ),
    ]

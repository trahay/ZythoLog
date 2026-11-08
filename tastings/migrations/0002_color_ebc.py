import django.core.validators
from django.db import migrations, models

# Valeur EBC représentative de chaque ancienne teinte
OLD_TO_EBC = {"paille": 4, "jaune": 8, "doree": 12, "ambree": 20, "cuivree": 28,
              "acajou": 40, "brune": 60, "noire": 80}


def forwards(apps, schema_editor):
    Tasting = apps.get_model("tastings", "Tasting")
    for t in Tasting.objects.exclude(color=""):
        t.color_ebc = OLD_TO_EBC.get(t.color)
        t.save(update_fields=["color_ebc"])


class Migration(migrations.Migration):
    dependencies = [("tastings", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="tasting",
            name="color_ebc",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="couleur (EBC)",
                validators=[django.core.validators.MinValueValidator(2),
                            django.core.validators.MaxValueValidator(80)]),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(model_name="tasting", name="color"),
    ]

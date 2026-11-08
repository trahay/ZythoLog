from decimal import Decimal

from django.db import migrations, models


def to_five(apps, schema_editor):
    # Note /10 → impression personnelle 1–5 (arrondi au plus proche, au moins 1)
    Tasting = apps.get_model("tastings", "Tasting")
    for t in Tasting.objects.only("pk", "rating"):
        new = max(1, min(5, int(Decimal(t.rating) / 2 + Decimal("0.5"))))
        Tasting.objects.filter(pk=t.pk).update(rating=new)


def to_ten(apps, schema_editor):
    Tasting = apps.get_model("tastings", "Tasting")
    for t in Tasting.objects.only("pk", "rating"):
        Tasting.objects.filter(pk=t.pk).update(rating=t.rating * 2)


class Migration(migrations.Migration):
    dependencies = [("tastings", "0009_mouthfeel_sensations")]

    operations = [
        migrations.RunPython(to_five, to_ten),
        migrations.AlterField(
            model_name="tasting", name="rating",
            field=models.PositiveSmallIntegerField(
                "impression personnelle",
                choices=[(1, "Pas pour moi"), (2, "Bof"), (3, "Agréable"), (4, "Très bonne"), (5, "Délicieuse")],
            ),
        ),
        migrations.AddField(
            model_name="tasting", name="balance",
            field=models.PositiveSmallIntegerField(
                "ensemble et équilibre", blank=True, null=True,
                choices=[(1, "Fade"), (2, "Quelconque"), (3, "Correct"), (4, "Réussi"), (5, "Remarquable")],
            ),
        ),
    ]

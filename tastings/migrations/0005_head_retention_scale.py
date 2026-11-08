from django.db import migrations, models

# Ancienne échelle 0 (nulle) … 4 (excellente) → 1 (pauvre) … 5 (persistante)
OLD_TO_NEW = {0: 1, 1: 1, 2: 2, 3: 3, 4: 5}
NEW_TO_OLD = {1: 1, 2: 2, 3: 3, 4: 3, 5: 4}


def remap(mapping):
    def run(apps, schema_editor):
        Tasting = apps.get_model("tastings", "Tasting")
        # Un seul passage par ligne pour ne pas re-transformer une valeur déjà convertie
        for t in Tasting.objects.exclude(head_retention=None).only("pk", "head_retention"):
            Tasting.objects.filter(pk=t.pk).update(head_retention=mapping[t.head_retention])
    return run


class Migration(migrations.Migration):
    dependencies = [("tastings", "0004_clarity_scale")]

    operations = [
        migrations.RunPython(remap(OLD_TO_NEW), remap(NEW_TO_OLD)),
        migrations.AlterField(
            model_name="tasting", name="head_retention",
            field=models.PositiveSmallIntegerField(
                "ténacité de la mousse", blank=True, null=True,
                choices=[(1, "Pauvre"), (2, "Moyenne"), (3, "Bonne"), (4, "Très bonne"), (5, "Persistante")],
            ),
        ),
    ]

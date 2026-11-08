from django.db import migrations, models

# Anciennes valeurs texte → nouvelle échelle 1 (claire) … 5 (opaque)
OLD_TO_NEW = {"brillante": 1, "limpide": 1, "voilee": 2, "trouble": 4, "opaque": 5}


def forwards(apps, schema_editor):
    Tasting = apps.get_model("tastings", "Tasting")
    for old, new in OLD_TO_NEW.items():
        Tasting.objects.filter(clarity=old).update(clarity_level=new)


def backwards(apps, schema_editor):
    Tasting = apps.get_model("tastings", "Tasting")
    for level, old in {1: "limpide", 2: "voilee", 3: "voilee", 4: "trouble", 5: "opaque"}.items():
        Tasting.objects.filter(clarity_level=level).update(clarity=old)


class Migration(migrations.Migration):
    dependencies = [("tastings", "0003_beer_style_list")]

    operations = [
        migrations.AddField(
            model_name="tasting", name="clarity_level",
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="tasting", name="clarity"),
        migrations.RenameField(model_name="tasting", old_name="clarity_level", new_name="clarity"),
        migrations.AlterField(
            model_name="tasting", name="clarity",
            field=models.PositiveSmallIntegerField(
                "transparence", blank=True, null=True,
                choices=[(1, "Claire"), (2, "Légèrement voilée"), (3, "Voilée"), (4, "Très voilée"), (5, "Opaque")],
            ),
        ),
    ]

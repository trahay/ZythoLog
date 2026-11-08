from django.db import migrations

# Anciens styles (saisie libre) -> style de la liste Wikipédia
OLD_TO_NEW = {
    "pils": "Pilsner allemande (pils)", "pilsner": "Pilsner allemande (pils)",
    "helles": "Munich Helles", "märzen": "Märzen / Oktoberfest",
    "witbier": "Blanche (witbier)", "blanche": "Blanche (witbier)",
    "weizen / hefeweizen": "Weizen / Weissbier", "weizen": "Weizen / Weissbier",
    "tripel": "Triple", "quadrupel": "Quadruple", "belgian strong ale": "Belge forte",
    "pale ale": "Pale ale américaine (APA)", "american pale ale": "Pale ale américaine (APA)",
    "ipa": "IPA américaine", "west coast ipa": "IPA américaine",
    "double ipa": "Imperial IPA (double IPA)", "neipa": "NEIPA / Hazy IPA (*)",
    "session ipa": "Session IPA (*)", "black ipa": "Black IPA (*)",
    "bitter": "Best bitter", "esb": "Extra special bitter (ESB) / English pale ale",
    "brown ale": "Northern English brown ale", "amber ale": "Ale ambrée américaine",
    "porter": "Robust porter", "stout": "Dry stout", "milk stout": "Sweet stout (milk stout)",
    "barley wine": "Barley wine britannique", "kriek": "Lambic aux fruits",
    "sour / wild ale": "Bière sauvage (Brett, fermentation mixte)",
    "fruit beer": "Bière aux fruits", "lager": "Lager standard américaine",
}


def forwards(apps, schema_editor):
    Beer = apps.get_model("tastings", "Beer")
    from tastings.choices import ALL_STYLES
    by_lower = {s.lower(): s for s in ALL_STYLES}
    for beer in Beer.objects.exclude(style=""):
        key = beer.style.strip().lower()
        new = OLD_TO_NEW.get(key) or by_lower.get(key)
        if new and new != beer.style:
            beer.style = new
            beer.save(update_fields=["style"])


class Migration(migrations.Migration):
    dependencies = [("tastings", "0002_color_ebc")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]

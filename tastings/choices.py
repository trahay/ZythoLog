"""Vocabulaire de la fiche de dégustation.

Inspiré de la fiche « Projet Amertume » (analyse sensorielle vue / odorat /
goût / toucher, descripteurs regroupés par origine, faux-goûts classés par
cause).
"""

# Arômes et saveurs : intensité et impression sur 5 points (curseurs)
SCALE_INTENSITY = [
    (1, "Faible"),
    (2, "Plutôt faible"),
    (3, "Moyenne"),
    (4, "Plutôt forte"),
    (5, "Forte"),
]
SCALE_INTENSITY_TICKS = ["Faible", "Moyenne", "Forte"]
SCALE_INTENSITY_GRADIENT = "linear-gradient(to right, #fbf1d3 0%, #f0c46a 50%, #c4661f 100%)"

SCALE_IMPRESSION = [
    (1, "Déplaisante"),
    (2, "Plutôt déplaisante"),
    (3, "Neutre"),
    (4, "Plutôt plaisante"),
    (5, "Plaisante"),
]
SCALE_IMPRESSION_TICKS = ["Déplaisante", "Neutre", "Plaisante"]
SCALE_IMPRESSION_GRADIENT = "linear-gradient(to right, #d9695f 0%, #e6e0d2 50%, #6fb36b 100%)"

SERVING = [
    ("bouteille", "Bouteille"),
    ("canette", "Canette"),
    ("pression", "Pression"),
    ("autre", "Autre"),
]

# --- Vue -------------------------------------------------------------------
# Couleur : échelle EBC (European Brewery Convention), 1 SRM ≈ 1,97 EBC.
EBC_MIN, EBC_MAX = 2, 80

# Couleur approximative de la bière pour chaque valeur SRM (1 à 40)
SRM_HEX = [
    "#FFE699", "#FFD878", "#FFCA5A", "#FFBF42", "#FBB123", "#F8A600", "#F39C00",
    "#EA8F00", "#E58500", "#DE7C00", "#D77200", "#CF6900", "#CB6200", "#C35900",
    "#BB5100", "#B54C00", "#B04500", "#A63E00", "#A13700", "#9B3200", "#952D00",
    "#8E2900", "#882300", "#821E00", "#7B1A00", "#771900", "#701400", "#6A0E00",
    "#660D00", "#5E0B00", "#5A0A02", "#600903", "#520907", "#4C0505", "#470606",
    "#440607", "#3F0708", "#3B0607", "#3A070B", "#36080A",
]

# Nom de la teinte : (EBC maximum, libellé)
EBC_LABELS = [
    (6, "Paille"),
    (9, "Jaune pâle"),
    (14, "Dorée"),
    (22, "Ambrée"),
    (32, "Cuivrée"),
    (45, "Acajou / rousse"),
    (70, "Brune"),
    (EBC_MAX, "Noire"),
]


def ebc_to_hex(ebc):
    srm = min(max(round(ebc / 1.97), 1), len(SRM_HEX))
    return SRM_HEX[srm - 1]


def ebc_label(ebc):
    return next(label for limit, label in EBC_LABELS if ebc <= limit)


def ebc_gradient():
    """Dégradé CSS couvrant toute l'échelle EBC du curseur."""
    stops = []
    for srm, hex_ in enumerate(SRM_HEX, start=1):
        pct = (srm * 1.97 - EBC_MIN) / (EBC_MAX - EBC_MIN) * 100
        if 0 <= pct <= 100:
            stops.append(f"{hex_} {pct:.1f}%")
    return f"linear-gradient(to right, {SRM_HEX[0]} 0%, {', '.join(stops)}, {SRM_HEX[-1]} 100%)"


# Transparence sur 5 points : claire → voilée → opaque
CLARITY = [
    (1, "Claire"),
    (2, "Légèrement voilée"),
    (3, "Voilée"),
    (4, "Très voilée"),
    (5, "Opaque"),
]
# Repères affichés sous le curseur
CLARITY_TICKS = ["Claire", "Voilée", "Opaque"]
# Dégradé du curseur : une bière dorée de plus en plus trouble
CLARITY_GRADIENT = ("linear-gradient(to right, #fff4c2 0%, #f3dc8e 25%, "
                    "#dcc58f 50%, #b9a98d 75%, #8a8172 100%)")

HEAD_COLOR = [
    ("blanche", "Blanche"),
    ("ivoire", "Ivoire / crème"),
    ("beige", "Beige"),
    ("brune", "Brune / moka"),
]

HEAD_TEXTURE = [
    ("fine", "Fine / crémeuse"),
    ("moyenne", "Moyenne"),
    ("grossiere", "Grossière / bulles larges"),
]

# Ténacité de la mousse sur 5 points : pauvre → bonne → persistante
HEAD_RETENTION = [
    (1, "Pauvre"),
    (2, "Moyenne"),
    (3, "Bonne"),
    (4, "Très bonne"),
    (5, "Persistante"),
]
HEAD_RETENTION_TICKS = ["Pauvre", "Bonne", "Persistante"]
# Dégradé du curseur : de quelques bulles à une mousse dense
HEAD_RETENTION_GRADIENT = ("linear-gradient(to right, #d9a93f 0%, #ead6a0 50%, #fffdf6 100%)")

# --- Toucher ---------------------------------------------------------------
BODY = [
    (1, "Très léger"),
    (2, "Léger"),
    (3, "Moyen"),
    (4, "Plein"),
    (5, "Très plein"),
]

CARBONATION = [
    (1, "Très faible"),
    (2, "Faible"),
    (3, "Moyenne"),
    (4, "Élevée"),
    (5, "Très élevée"),
]

BODY_TICKS = ["Très léger", "Moyen", "Très plein"]
BODY_GRADIENT = "linear-gradient(to right, #fbf3dc 0%, #e8c477 50%, #a9652a 100%)"
CARBONATION_TICKS = ["Très faible", "Moyenne", "Très élevée"]
CARBONATION_GRADIENT = "linear-gradient(to right, #efe9dc 0%, #bcd8e6 50%, #5fa3cc 100%)"

# Sensations en bouche (cases à cocher)
MOUTHFEEL_SENSATIONS = [
    ("astringente", "Astringente"),
    ("chauffante", "Chauffante"),
    ("cremeuse", "Crémeuse"),
    ("sirupeuse", "Sirupeuse"),
    ("piquante", "Piquante"),
    ("veloutee", "Veloutée"),
    ("moelleuse", "Moelleuse"),
    ("seche", "Sèche"),
    ("surette", "Surette"),
]
MOUTHFEEL_SENSATION_LABELS = dict(MOUTHFEEL_SENSATIONS)

# Verdict (curseurs sur 5 points)
PERSONAL_IMPRESSION = [
    (1, "Pas pour moi"),
    (2, "Bof"),
    (3, "Agréable"),
    (4, "Très bonne"),
    (5, "Délicieuse"),
]
PERSONAL_IMPRESSION_TICKS = ["Pas pour moi", "Agréable", "Délicieuse"]
PERSONAL_IMPRESSION_GRADIENT = "linear-gradient(to right, #e6e0d2 0%, #f3d27a 50%, #e07b2c 100%)"

BALANCE = [
    (1, "Fade"),
    (2, "Quelconque"),
    (3, "Correct"),
    (4, "Réussi"),
    (5, "Remarquable"),
]
BALANCE_TICKS = ["Fade", "Correct", "Remarquable"]
BALANCE_GRADIENT = "linear-gradient(to right, #e6e0d2 0%, #c9d6a3 50%, #6f9f4a 100%)"

FINISH = [
    ("court", "Courte"),
    ("moyen", "Moyenne"),
    ("long", "Longue"),
]

# --- Descripteurs de flaveurs (arômes et saveurs), groupés par origine -----
DESCRIPTORS = [
    ("Céréales / malt", [
        ("cereale", "Céréale crue"),
        ("pain", "Pain / mie"),
        ("biscuit", "Biscuit"),
        ("miel", "Miel"),
        ("caramel", "Caramel"),
        ("toffee", "Toffee"),
        ("fruits_secs", "Fruits secs"),
        ("torrefie", "Torréfié / grillé"),
        ("cafe", "Café"),
        ("chocolat", "Chocolat / cacao"),
        ("fume", "Fumé"),
    ]),
    ("Houblon", [
        ("agrumes", "Agrumes"),
        ("tropical", "Fruits tropicaux"),
        ("fruits_jaunes", "Fruits jaunes"),
        ("fruits_rouges_h", "Fruits rouges"),
        ("resineux", "Résineux / pin"),
        ("herbace", "Herbacé"),
        ("floral", "Floral"),
        ("epice_h", "Épicé / poivré"),
        ("terreux", "Terreux"),
    ]),
    ("Levures / fermentation", [
        ("banane", "Banane"),
        ("girofle", "Clou de girofle"),
        ("fruite", "Fruité (esters)"),
        ("poivre", "Poivre (phénols)"),
        ("lactique", "Lactique / acidulé"),
        ("brett", "Funky / Brett"),
        ("vineux", "Vineux"),
    ]),
    ("Eau / minéralité", [
        ("mineral", "Minéral"),
        ("sale", "Salé"),
        ("souffre", "Soufré"),
    ]),
    ("Épices et ajouts", [
        ("coriandre", "Coriandre"),
        ("orange", "Écorce d'orange"),
        ("vanille", "Vanille"),
        ("cannelle", "Cannelle"),
        ("fruits_ajoutes", "Fruits ajoutés"),
    ]),
    ("Élevage en fût", [
        ("boise", "Boisé / chêne"),
        ("whisky", "Whisky / bourbon"),
        ("vin", "Vin"),
        ("coco", "Noix de coco"),
    ]),
]

# Styles de bière, d'après https://fr.wikipedia.org/wiki/Liste_des_styles_de_bière
# (classement « Détails de certains types de bières » et « Hybrides et bières
# spéciales »). Les styles marqués « (*) » n'y figurent pas mais sont courants.
BEER_STYLES = [
    ("Ales américaines", [
        "Pale ale américaine (APA)", "Ale ambrée américaine", "Brown ale américaine",
    ]),
    ("Ale québécoise", ["Annedd'ale"]),
    ("Ales fortes", ["Old ale", "Barley wine britannique", "Barley wine américain"]),
    ("Belges", [
        "Blanche (witbier)", "Pale ale belge", "Saison", "Bière de garde", "Spéciale belge",
    ]),
    ("Belges fortes", ["Blonde belge", "Dubbel", "Triple", "Belge forte", "Quadruple"]),
    ("Bières acidulées", [
        "Berliner Weisse", "Rouge de Flandres", "Brune de Flandres (oud bruin)", "Lambic",
        "Gueuze", "Lambic aux fruits", "Gose",
    ]),
    ("Bitter et pale ale", [
        "Ordinary bitter", "Best bitter", "Extra special bitter (ESB) / English pale ale",
    ]),
    ("Bock", ["Maibock / Helles bock", "Bock", "Doppelbock", "Eisbock"]),
    ("Brown ale", ["Mild", "Southern English brown ale", "Northern English brown ale"]),
    ("Hybrides ambrées", ["Altbier du nord", "California common (steam beer)", "Altbier de Düsseldorf"]),
    ("Hybrides blondes", ["Cream ale", "Ale blonde", "Kölsch", "Bière de blé ou de seigle américaine"]),
    ("India pale ale (IPA)", [
        "IPA britannique", "IPA américaine", "Imperial IPA (double IPA)",
        "NEIPA / Hazy IPA (*)", "Session IPA (*)", "Black IPA (*)",
    ]),
    ("Lagers ambrées", ["Viennoise", "Märzen / Oktoberfest", "Rauchbier"]),
    ("Lagers blondes", [
        "American light lager", "Lager standard américaine", "Lager premium américaine",
        "Munich Helles", "Dortmunder export",
    ]),
    ("Lagers foncées", ["Lager foncée américaine", "Munich Dunkel", "Schwarzbier"]),
    ("Pilsner", ["Pilsner allemande (pils)", "Pilsner bohémienne", "Pilsner américaine classique"]),
    ("Porter", ["Brown porter", "Robust porter", "Porter baltique"]),
    ("Scottish et Irish ale", [
        "Scottish light 60/-", "Scottish heavy 70/-", "Scottish export 80/-",
        "Irish red ale", "Scotch ale",
    ]),
    ("Stout", [
        "Dry stout", "Sweet stout (milk stout)", "Oatmeal stout", "Foreign extra stout",
        "Stout américaine", "Imperial stout",
    ]),
    ("Weizen", ["Weizen / Weissbier", "Dunkelweizen", "Weizenbock", "Roggenbier"]),
    ("Bières spéciales", [
        "Bière aux fruits", "Bière aux herbes et épices", "Bière au miel",
        "Bière aux céréales alternatives", "Bière fumée", "Bière aux légumes (citrouille…)",
        "Bière sauvage (Brett, fermentation mixte)", "Bière vieillie en fût",
    ]),
    ("Boissons apparentées", ["Gruit", "Sahti", "Kvas", "Braggot"]),
    ("Autre", ["Autre style"]),
]

ALL_STYLES = [style for _, styles in BEER_STYLES for style in styles]


def style_choices():
    """Choix groupés pour un <select> (valeur = libellé)."""
    return [("", "— Choisir un style —")] + [
        (group, [(s, s) for s in styles]) for group, styles in BEER_STYLES
    ]



def flatten(grouped):
    return {k: v for _, items in grouped for k, v in items}


DESCRIPTOR_LABELS = flatten(DESCRIPTORS)

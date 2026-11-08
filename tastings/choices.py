"""Vocabulaire de la fiche de dégustation.

Inspiré de la fiche « Projet Amertume » (analyse sensorielle vue / odorat /
goût / toucher, descripteurs regroupés par origine, faux-goûts classés par
cause).
"""

INTENSITY = [
    (0, "0 – absent"),
    (1, "1 – très faible"),
    (2, "2 – faible"),
    (3, "3 – moyen"),
    (4, "4 – fort"),
    (5, "5 – très fort"),
]

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


CLARITY = [
    ("brillante", "Brillante"),
    ("limpide", "Limpide"),
    ("voilee", "Légèrement voilée"),
    ("trouble", "Trouble"),
    ("opaque", "Opaque"),
]

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

HEAD_RETENTION = [
    (0, "Nulle"),
    (1, "Faible"),
    (2, "Moyenne"),
    (3, "Bonne"),
    (4, "Excellente"),
]

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

OFF_FLAVORS = [
    ("Ingrédients", [
        ("dms", "DMS (maïs cuit, légumes)"),
        ("astringent", "Astringence (tanins)"),
    ]),
    ("Processus de brassage", [
        ("diacetyle", "Diacétyle (beurre)"),
        ("acetaldehyde", "Acétaldéhyde (pomme verte)"),
        ("solvant", "Solvant / alcools supérieurs"),
        ("autolyse", "Autolyse (levure, viande)"),
    ]),
    ("Infections microbiologiques", [
        ("acetique", "Acétique (vinaigre)"),
        ("phenolique", "Phénolique (médicinal, plastique)"),
        ("aigre", "Aigre non voulu"),
    ]),
    ("Garde et conditionnement", [
        ("oxydation", "Oxydation (carton, xérès)"),
        ("lumiere", "Goût de lumière (skunky)"),
        ("metallique", "Métallique"),
        ("bouchon", "Bouchon / moisi"),
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
OFF_FLAVOR_LABELS = flatten(OFF_FLAVORS)

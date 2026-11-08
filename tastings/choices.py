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

COMMON_STYLES = [
    "Lager", "Pils", "Helles", "Märzen", "Bock", "Doppelbock", "Schwarzbier",
    "Witbier", "Weizen / Hefeweizen", "Saison", "Blonde belge", "Dubbel",
    "Tripel", "Quadrupel", "Belgian Strong Ale", "Bière de garde",
    "Pale Ale", "American Pale Ale", "IPA", "West Coast IPA", "NEIPA",
    "Double IPA", "Session IPA", "Black IPA", "Bitter", "ESB", "Amber Ale",
    "Brown Ale", "Porter", "Stout", "Imperial Stout", "Oatmeal Stout",
    "Milk Stout", "Barley Wine", "Scotch Ale", "Berliner Weisse", "Gose",
    "Lambic", "Gueuze", "Kriek", "Sour / Wild Ale", "Fruit Beer",
]


def flatten(grouped):
    return {k: v for _, items in grouped for k, v in items}


DESCRIPTOR_LABELS = flatten(DESCRIPTORS)
OFF_FLAVOR_LABELS = flatten(OFF_FLAVORS)

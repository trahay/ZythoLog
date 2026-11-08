# ZythoLog — carnet de dégustation de bières (Django)

## Lancer l'application

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # optionnel, pour /admin/
.venv/bin/python manage.py runserver
```

Puis ouvrir http://localhost:8000. Tests : `.venv/bin/python manage.py test tastings`.

## Organisation

- `tastings/models.py` : `Brewery`, `Beer` (nom + brasserie unique, style, degré, IBU),
  `Tasting` (la fiche de dégustation) et `Photo` (plusieurs photos par fiche).
- `tastings/choices.py` : tout le vocabulaire de la fiche (couleurs, transparence,
  ténacité de la mousse, échelles d'intensité 0–5, descripteurs groupés par origine
  — céréales, houblon, levures, eau, épices, fût — et faux-goûts classés par cause).
  C'est le fichier à modifier pour adapter la fiche.
- `tastings/forms.py` : le formulaire crée la bière et la brasserie à la volée
  (recherche insensible à la casse), gère l'upload multiple de photos.
- `tastings/ownership.py` + `signals.py` : dégustations sans compte.

## Dégustations sans compte

- Un visiteur non connecté peut saisir une fiche (avec un pseudo facultatif).
  L'identifiant de la fiche est conservé dans sa session : il la retrouve dans
  « Mes dégustations » et peut la modifier/supprimer depuis ce navigateur.
- Chaque fiche anonyme a un **lien secret** (`/degustations/acces/<jeton>/`) affiché
  à son auteur, pour la retrouver depuis un autre navigateur.
- À la connexion ou à la création d'un compte, les fiches anonymes de la session
  sont automatiquement rattachées au compte.

## Avant une mise en production

définir les variables d'environnement `DJANGO_SECRET_KEY` (clé aléatoire),
`DJANGO_DEBUG=0` et `DJANGO_ALLOWED_HOSTS` (ex. `zytholog.example.org`),
servir `media/` (photos) et les fichiers statiques via le serveur web
(`collectstatic`), et idéalement une base PostgreSQL.

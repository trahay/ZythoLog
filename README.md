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

## Déploiement avec Docker

La pile `docker-compose.yml` lance trois conteneurs :

- `web` : Django servi par gunicorn (migrations et `collectstatic` au démarrage) ;
- `nginx` : sert les fichiers statiques et les photos, transmet le reste à Django,
  et écoute uniquement en local sur `127.0.0.1:${ZYTHOLOG_PORT}` (9003 par défaut) ;
- `postgres` : la base de données.

L'appli est prévue pour être servie sous un préfixe (`/zytholog` par défaut,
variable `ZYTHOLOG_PATH`) derrière un reverse proxy HTTPS (YunoHost).

```bash
cp .env.sample .env   # puis remplir les secrets
docker compose up -d --build
docker compose exec web python manage.py createsuperuser   # compte admin
```

Mise à jour : `git pull && docker compose up -d --build`.

Données persistantes (volumes Docker) : `postgres_data` (base) et `media` (photos).
Sauvegarde de la base :

```bash
docker compose exec postgres pg_dump -U zytholog zytholog > zytholog.sql
```

### Connexion avec Google (facultatif)

1. Dans la [console Google Cloud](https://console.cloud.google.com/apis/credentials),
   configurer l'écran de consentement OAuth (type « Externe »), puis créer un
   identifiant « ID client OAuth » de type « Application Web ».
2. URI de redirection autorisé :
   `https://trahay.nohost.me/zytholog/accounts/google/login/callback/`
3. Reporter l'ID client et le code secret dans `.env` (`GOOGLE_CLIENT_ID`,
   `GOOGLE_CLIENT_SECRET`), puis `docker compose up -d`.

Sans ces deux variables, le bouton « Se connecter avec Google » n'apparaît pas.
Une connexion Google crée un compte ZythoLog au premier passage et y rattache
les dégustations faites sans compte depuis le même navigateur.

### Côté YunoHost

Installer l'appli « Redirect » sur `trahay.nohost.me/zytholog`, en mode
reverse proxy vers `http://127.0.0.1:9003/zytholog`, visible par les visiteurs
(public) pour qu'on puisse noter sans compte.

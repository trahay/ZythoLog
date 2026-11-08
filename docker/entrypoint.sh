#!/bin/sh
set -e

# Applique les migrations et publie les fichiers statiques à chaque démarrage
python manage.py migrate --noinput
python manage.py collectstatic --noinput --verbosity 0

exec "$@"

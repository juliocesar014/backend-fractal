#!/bin/bash
set -e

python manage.py migrate

python manage.py loaddata fixture-db.json

exec "$@"

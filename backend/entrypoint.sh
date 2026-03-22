#!/bin/sh
set -e

# Run migration
python manage.py migrate

# Fill db with defauld data
python manage.py set_base_data

# Run container main process
exec "$@"

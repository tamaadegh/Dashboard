#!/bin/sh

set -e

python manage.py migrate

gunicorn nxtbn.wsgi:application --bind :8000

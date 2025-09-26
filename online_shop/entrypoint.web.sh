#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn online_shop.wsgi:application --bind 0.0.0.0:8000 
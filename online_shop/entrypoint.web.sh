#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn -c gunicorn.conf.py online_shop.wsgi:application
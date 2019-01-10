#!/bin/bash
python3 /app/manage.py migrate --settings=MusicManager.settings.$1
gunicorn MusicManager.wsgi:application --bind=0.0.0.0:8000
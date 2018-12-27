#!/bin/bash
python3 /app/manage.py migrate --settings=MusicManager.settings.preproduction
python3 /app/manage.py runserver 0.0.0.0:8000 --settings=MusicManager.settings.preproduction
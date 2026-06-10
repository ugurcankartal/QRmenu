@echo off
cd /d %~dp0
set DJANGO_SETTINGS_MODULE=config.settings.prod
venv\Scripts\python.exe manage.py runserver

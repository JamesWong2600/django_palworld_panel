@echo off
call venv\Scripts\activate
cd panel_project
python manage.py runserver
pause
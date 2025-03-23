@echo off
REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements if they exist
IF EXIST "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Change directory and start server
cd panel_project
python manage.py runserver

pause
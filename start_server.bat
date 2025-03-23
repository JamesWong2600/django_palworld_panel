@echo off
setlocal enabledelayedexpansion

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    winget install Python.Python.3.11
    if !errorlevel! neq 0 (
        echo Failed to install Python. Please install manually from python.org
        pause
        exit /b 1
    )
    echo Python installed successfully.
    REM Refresh PATH
    refreshenv
)


REM Check if pip is installed
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
    if !errorlevel! neq 0 (
        echo Failed to install pip. Please install manually.
        pause
        exit /b 1
    )
    echo pip installed successfully.
    REM Refresh PATH
    refreshenv
)



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
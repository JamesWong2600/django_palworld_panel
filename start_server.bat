@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    REM Try to install Python using winget
    winget install --id Python.Python.3.11 --source winget
    if !errorlevel! neq 0 (
        echo Winget installation failed, trying alternative download method...
        REM Download Python installer directly
        curl -o python_installer.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
        REM Install Python with required options
        python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        REM Clean up installer
        del python_installer.exe
        if !errorlevel! neq 0 (
            echo Failed to install Python. Please install manually from python.org
            pause
            exit /b 1
        )
    )
    echo Python installed successfully.
    REM Refresh PATH
    call set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
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
    call set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
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
    python -m pip install -r requirements.txt
)

REM Change directory and start server
cd panel_project
python manage.py runserver

pause
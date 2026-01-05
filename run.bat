@echo off
echo ========================================
echo SSH Manager API - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists (check both venv and myenv)
if not exist venv (
    if not exist myenv (
        echo Creating virtual environment...
        python -m venv venv
        echo Virtual environment created!
        echo.
    ) else (
        echo Using existing virtual environment: myenv
        call myenv\Scripts\activate.bat
        goto :skip_venv
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:skip_venv

REM Check if dependencies are installed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed!
    echo.
) else (
    echo Dependencies already installed.
    echo.
)

REM Create uploads directory if it doesn't exist
if not exist uploads mkdir uploads

echo ========================================
echo Starting SSH Manager API...
echo ========================================
echo.
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause


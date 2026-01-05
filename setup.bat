@echo off
echo Setting up SSH Manager API...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Create uploads directory
if not exist uploads mkdir uploads

REM Create .env file if it doesn't exist
if not exist .env (
    copy env_template.txt .env
    echo.
    echo .env file created. Please edit it with your configuration.
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run: python main.py
echo 3. Access API at http://localhost:8000
echo 4. View docs at http://localhost:8000/docs
echo.
pause


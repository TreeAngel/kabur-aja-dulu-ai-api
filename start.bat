@echo off

echo =====================================
echo Activating virtual environment...
echo =====================================

call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Checking dependencies...
echo =====================================

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Failed to install required packages.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Starting KaburAjaDulu.AI API Server
echo =====================================
echo Docs   : http://localhost:8000/docs
echo Health : http://localhost:8000/health
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
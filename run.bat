@echo off
REM ==========================
REM Auto-deploy SymptomX Site
REM ==========================

REM Change to the project directory (edit the path if needed)
cd /d "%~dp0symptomx-remade"

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================
echo Starting SymptomX Flask server...
echo Open http://127.0.0.1:5000 in your browser
echo ================================
echo.

python app.py

pause

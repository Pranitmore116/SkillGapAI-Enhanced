@echo off
echo =============================================
echo   SkillGapAI - Starting Python Backend
echo   CSE472: Deep Learning for NLP (2026-27)
echo =============================================

:: Navigate to the backend folder relative to this script
cd /d "%~dp0backend"

:: Try .venv first, fall back to system python
if exist "%~dp0.venv\Scripts\python.exe" (
    echo Using virtual environment: %~dp0.venv
    "%~dp0.venv\Scripts\python.exe" app.py
) else (
    echo Virtual environment not found. Using system Python...
    echo Run: python -m venv .venv ^& .venv\Scripts\activate ^& pip install -r backend\requirements.txt
    python app.py
)
pause

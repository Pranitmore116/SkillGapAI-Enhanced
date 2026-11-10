@echo off
echo =============================================
echo   SkillGapAI - Starting Frontend Web Server
echo =============================================

cd /d "%~dp0"
echo Serving from %CD% ...
echo Opening SkillGapAI in your default browser...
start "" http://localhost:8080/SkillGapAI-Frontend/index.html

python -m http.server 8080
pause


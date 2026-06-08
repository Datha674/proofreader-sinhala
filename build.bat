@echo off
chcp 65001 >nul
title Build SinhalaProofreader.exe
cd /d "%~dp0"
echo ========================================
echo   Building SinhalaProofreader.exe
echo ========================================
echo.
echo Installing/refreshing dependencies...
pip install -r requirements.txt --quiet
echo.
echo Running PyInstaller...
python -m PyInstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo BUILD FAILED. See messages above.
    pause & exit /b 1
)
echo.
echo ========================================
echo   DONE -> dist\SinhalaProofreader.exe
echo ========================================
pause

@echo off
chcp 65001 >nul
title Autostart Setup - Sinhala Proxy
schtasks /create /tn "SinhalaProofreadProxy" /tr "\"%~dp0START_PROXY.bat\"" /sc onlogon /ru "%USERNAME%" /f
if errorlevel 1 (
    echo FAILED. Try running as administrator.
) else (
    echo Proxy will now auto-start when this user logs in to Windows.
)
pause

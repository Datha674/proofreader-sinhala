@echo off
chcp 65001 >nul
title Firewall Setup - Sinhala Proxy

rem --- Self-elevate to Administrator if we are not already ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator rights...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

echo Adding Windows Firewall rule for TCP port 8765 (all network profiles)...
rem profile=any covers Public/Private/Domain — a fresh bridged VM is often
rem classified as "Public", which a private-only rule would NOT match.
netsh advfirewall firewall delete rule name="SinhalaProofreadProxy" >nul 2>&1
netsh advfirewall firewall add rule name="SinhalaProofreadProxy" dir=in action=allow protocol=TCP localport=8765 profile=any
if errorlevel 1 (
    echo.
    echo FAILED to add the rule. Make sure you approved the Administrator prompt.
) else (
    echo.
    echo Done. Clients on the LAN can now reach this PC on port 8765.
)
echo.
pause

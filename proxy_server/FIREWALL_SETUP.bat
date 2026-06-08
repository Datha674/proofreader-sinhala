@echo off
chcp 65001 >nul
title Firewall Setup - Sinhala Proxy
echo Adding Windows Firewall rule for TCP port 8765 (private networks)...
netsh advfirewall firewall add rule name="SinhalaProofreadProxy" dir=in action=allow protocol=TCP localport=8765 profile=private
if errorlevel 1 (
    echo.
    echo FAILED. Right-click this file and choose "Run as administrator".
) else (
    echo.
    echo Done. Clients on the LAN can now reach port 8765.
)
pause

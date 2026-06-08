@echo off
chcp 65001 >nul
title Stop Sinhala Proxy
taskkill /fi "WINDOWTITLE eq SinhalaProxyServer" /f >nul 2>&1
echo Proxy server stopped (any window titled SinhalaProxyServer).
echo If it is still running, close its console window manually.
pause

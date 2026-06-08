@echo off
chcp 65001 >nul
title Control PC LAN IP
echo Your Control PC LAN IP address(es):
echo (Give the matching one to all client PCs)
echo ================================
ipconfig | findstr /i "IPv4"
echo ================================
echo Clients should set their Proxy URL to:
echo http://[IPv4 shown above]:8765
echo Example:  http://192.168.1.100:8765
pause

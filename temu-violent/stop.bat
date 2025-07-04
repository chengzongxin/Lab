@echo off
chcp 65001 >nul
echo ========================================
echo           停止项目服务
echo ========================================
echo.

echo [信息] 正在停止后端服务...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Backend Server*" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *backend*" >nul 2>&1

echo [信息] 正在停止前端服务...
taskkill /f /im node.exe /fi "WINDOWTITLE eq Frontend Server*" >nul 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *frontend*" >nul 2>&1

echo [信息] 正在停止相关进程...
taskkill /f /im python.exe /fi "COMMANDLINE eq *main.py*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *uvicorn*" >nul 2>&1
taskkill /f /im node.exe /fi "COMMANDLINE eq *vite*" >nul 2>&1

echo.
echo [信息] 服务已停止！
echo [提示] 如果仍有进程在运行，请手动关闭对应的命令行窗口
echo.
pause 
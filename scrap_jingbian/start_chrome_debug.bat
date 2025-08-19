@echo off
echo 启动Chrome浏览器（带调试端口）
echo.

REM 查找Chrome安装路径
set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else (
    echo 未找到Chrome浏览器，请手动安装或检查路径
    pause
    exit /b 1
)

echo 找到Chrome: %CHROME_PATH%
echo.
echo 启动Chrome浏览器，调试端口: 9222
echo 注意：这将关闭所有现有的Chrome窗口
echo.

REM 关闭现有的Chrome进程
taskkill /f /im chrome.exe >nul 2>&1
timeout /t 2 >nul

REM 启动Chrome，带调试端口
%CHROME_PATH% --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome_debug_profile"

echo.
echo Chrome已启动，调试端口: 9222
echo 现在可以运行爬虫程序，选择使用现有浏览器
pause

@echo off
chcp 65001 >nul
echo ========================================
echo           Temu Violent 项目启动器
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo [信息] 检测到Python和Node.js环境
echo.

:: 启动后端服务
echo [信息] 正在启动后端服务...
echo [信息] 后端服务将在 http://localhost:8000 启动
echo.

cd backend

echo [信息] 安装后端依赖...
pip install -r requirements.txt

echo [信息] 启动后端服务...
start "Backend Server" cmd /k "cd /d %cd% && python -m uvicorn main:app --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端服务
echo [信息] 正在启动前端服务...
echo [信息] 前端服务将在 http://localhost:5173 启动
echo.

cd ..\frontend

echo [信息] 安装前端依赖...
if not exist "node_modules" (
    npm install
)

echo [信息] 启动前端服务...
start "Frontend Server" cmd /k "cd /d %cd% && npm run dev"

:: 等待前端启动
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo           启动完成！
echo ========================================
echo.
echo [信息] 后端服务: http://localhost:8000
echo [信息] 前端服务: http://localhost:5173
echo.
echo [提示] 请等待几秒钟让服务完全启动
echo [提示] 按任意键打开浏览器访问前端页面
echo.
pause

:: 打开浏览器
start http://localhost:5173

echo.
echo [信息] 已打开浏览器，项目启动完成！
echo [提示] 关闭此窗口不会停止服务，服务将在后台继续运行
echo [提示] 如需停止服务，请关闭对应的命令行窗口
echo.
pause 
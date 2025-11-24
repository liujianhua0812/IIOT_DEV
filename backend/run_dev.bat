@echo off
REM 开发模式启动脚本（Windows 批处理版本）
cd /d %~dp0
call venv\Scripts\activate.bat
set FLASK_ENV=development
set DB_HOST=166.111.80.127
set DB_PORT=15432
python run_dev.py
pause


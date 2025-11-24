@echo off
REM AVI 转 MP4 视频转换脚本 (Windows 批处理版本)
cd /d %~dp0

echo ========================================
echo AVI 转 MP4 视频转换工具
echo ========================================
echo.

REM 检查是否在虚拟环境中
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM 运行转换脚本
python convert_avi_to_mp4.py %*

pause


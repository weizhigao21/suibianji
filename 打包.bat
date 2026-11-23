@echo off
chcp 65001 >nul
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title 随便记 一键打包
cd /d "%~dp0"
echo ============================================
echo    随便记 一键打包 ^(PyInstaller 单文件^)
echo ============================================
echo.

if not exist "suibianji.spec" (
    echo [错误] 未找到 suibianji.spec，请确认在项目根目录运行。
    goto fail
)

rem 优先使用项目虚拟环境，然后尝试 Python 3.10 和其他 Python 3。
set "PYCMD="
if not exist ".venv\Scripts\python.exe" goto find_python
".venv\Scripts\python.exe" -c "import sys, struct; sys.exit(0 if sys.version_info >= (3,10) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if not errorlevel 1 set PYCMD="%~dp0.venv\Scripts\python.exe"
if defined PYCMD goto python_ready
echo [提示] 项目虚拟环境已失效，正在查找本机可用的 Python…
:find_python
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3.10 -c "import sys, struct; sys.exit(0 if sys.version_info >= (3,10) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if not errorlevel 1 set "PYCMD=py -3.10"
if defined PYCMD goto python_ready
py -3 -c "import sys, struct; sys.exit(0 if sys.version_info >= (3,10) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if not errorlevel 1 set "PYCMD=py -3"
if defined PYCMD goto python_ready
:try_python
where python >nul 2>nul
if not errorlevel 1 set "PYCMD=python"
if not defined PYCMD (
    echo [错误] 未找到 Python，请安装 Python 3.10+ 并添加到 PATH。
    goto fail
)
:python_ready
%PYCMD% -c "import sys, struct; sys.exit(0 if sys.version_info >= (3,10) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if errorlevel 1 (
    echo [错误] 需要 64 位 Python 3.10+。请检查项目虚拟环境或 Python 安装。
    goto fail
)
echo [1/5] 使用 Python: %PYCMD%
%PYCMD% --version
echo.

rem 有些虚拟环境没有安装 pip；使用 Python 自带的离线安装器修复。
%PYCMD% -m pip --version >nul 2>nul
if errorlevel 1 (
    echo [1/5] 当前环境缺少 pip，正在自动修复…
    %PYCMD% -m ensurepip --upgrade
    if errorlevel 1 (
        echo [错误] 无法自动安装 pip。请修复 Python 安装，确保包含 pip 和 ensurepip 后重试。
        goto fail
    )
)
%PYCMD% -m pip --version >nul 2>nul
if errorlevel 1 (
    echo [错误] pip 修复后仍不可用，请检查上方安装日志。
    goto fail
)

%PYCMD% -c "import cryptography, keyring, PyQt6" >nul 2>nul
if errorlevel 1 (
    echo [2/5] 安装运行依赖…
    %PYCMD% -m pip install -r requirements.txt
    if errorlevel 1 goto fail
) else (
    echo [2/5] 运行依赖已就绪
)
%PYCMD% -c "from importlib.metadata import version; v=tuple(int(n) for n in version('pyinstaller').split('.')[:2]); assert (6,10) <= v and v[0] < 7" >nul 2>nul
if errorlevel 1 (
    echo [3/5] 安装 PyInstaller…
    %PYCMD% -m pip install "pyinstaller>=6.10,<7"
    if errorlevel 1 goto fail
) else (
    echo [3/5] PyInstaller 已就绪
)

echo [4/5] 开始打包…
%PYCMD% -m PyInstaller --noconfirm --clean suibianji.spec
if errorlevel 1 goto fail
if not exist "dist\随便记.exe" (
    echo [错误] 未生成 dist\随便记.exe，请查看上方 PyInstaller 日志。
    goto fail
)

echo [5/5] 生成版本 ZIP…
powershell -NoProfile -Command "Set-Location 'dist'; $exe = Get-ChildItem -Filter *.exe | Select-Object -First 1; if (-not $exe) { exit 1 }; Compress-Archive -LiteralPath $exe.Name -DestinationPath 'suibianji-1.0.0-win64.zip' -Force"
if errorlevel 1 (
    echo [提示] ZIP 生成失败，可直接分发 dist\随便记.exe。
) else (
    echo 版本 ZIP: %~dp0dist\suibianji-1.0.0-win64.zip
)

echo.
echo ============================================
echo    打包完成！
echo ============================================
echo 产物目录: %~dp0dist\
echo 主程序:   %~dp0dist\随便记.exe
echo 版本 ZIP: %~dp0dist\suibianji-1.0.0-win64.zip
echo.
echo 请分发上面生成的 EXE 或版本 ZIP，首次运行无需安装 Python。
echo data 目录优先使用 exe 同级 data，不可写时回退到 %%APPDATA%%\Suibianji\data，已存在的记录不会被覆盖。
echo 分发时不要打包 data 目录，避免把加密记录和设置一起发出去。
echo 升级时保留旧 data 目录即可继续使用原主密码登录。
echo.
if /i "%~1"=="--no-pause" exit /b 0
explorer "%~dp0dist" >nul 2>nul
pause
exit /b 0

:fail
echo.
echo [错误] 打包未完成，请查看上方日志定位原因。
if /i "%~1"=="--no-pause" exit /b 1
pause
exit /b 1

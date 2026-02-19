@echo on
setlocal

REM Get the directory of this script
set "PROJ_DIR=%~dp0"
REM Remove trailing backslash if exists
if "%PROJ_DIR:~-1%"=="\" set "PROJ_DIR=%PROJ_DIR:~0,-1%"

@REM REM Get site-packages directory using Python
@REM for /f "delims=" %%i in ('python -BEs -c "import site; print(site.getsitepackages()[0])"') do set "PY_DIR=%%i"
set "PY_DIR=%APPDATA%\Python\Python39\site-packages\"

set "ITVIEW_DIR=%PY_DIR%\itview"
REM set "RV_SUPPORT_PATH=%RV_SUPPORT_PATH%;%RV_HOME%\itview"

@REM set "APP_PLUGINS_1=%ITVIEW_DIR%\skin\plugins\plugin_paths_1.json"
@REM set "APP_PLUGINS_2=%ITVIEW_DIR%\skin\plugins\plugin_paths_2.json"
@REM set "ITVIEW_PLUGINS=APP:%APP_PLUGINS_1%, APP:%APP_PLUGINS_2%, %ITVIEW_PLUGINS%"
set "ITVIEW_PLUGINS=APP:%ITVIEW_DIR%\itview5_plugins\itview_plugin_paths.json"

REM Show only critical Qt errors in release build
set "QT_LOGGING_RULES=*=false;qt.core.critical=true;qt.core.fatal=true"
set "QTWEBENGINE_DISABLE_SANDBOX=1"
set "SUB_EXE=%ITVIEW_DIR%\sub\sub.py"

REM Run the main script with all arguments
python "%PROJ_DIR%\main.py" %*

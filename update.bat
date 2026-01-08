@echo off
setlocal EnableDelayedExpansion

echo ===============================
echo PKL PIPELINE UPDATER
echo ===============================

:: Configuración del Repo
set REPO_OWNER=FranzVega
set REPO_NAME=FV_Pipeline
set REPO_BRANCH=main

:: URLs
set REPO_ZIP_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/archive/refs/heads/%REPO_BRANCH%.zip
set REMOTE_VERSION_URL=https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/%REPO_BRANCH%/version.txt
set REMOTE_BAT_URL=https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/%REPO_BRANCH%/update.bat

:: Rutas Locales
set PIPELINE_ROOT=%~dp0
set ZIP_FILE=%TEMP%\pkl_pipeline_update.zip
set TEMP_REMOTE_VERSION=%TEMP%\pkl_remote_version.txt
set LOCAL_VERSION_FILE=%PIPELINE_ROOT%\version.txt
set CURRENT_BAT=%~f0

echo Checking version...

:: 1. Leer versión local y limpiar espacios 
if exist "%LOCAL_VERSION_FILE%" (
    set /p RAW_LOCAL=<"%LOCAL_VERSION_FILE%"
    set LOCAL_VERSION=!RAW_LOCAL: =!
) else (
    set LOCAL_VERSION=0.0.0
)

:: 2. Descargar versión remota
:: Usamos -s para que sea silencioso 
curl -L -s -o "%TEMP_REMOTE_VERSION%" "%REMOTE_VERSION_URL%"
if errorlevel 1 (
    echo Error: Could not connect to GitHub to check version.
    goto ERROR
)

:: 3. Leer versión remota y limpiar espacios 
set /p RAW_REMOTE=<"%TEMP_REMOTE_VERSION%"
set REMOTE_VERSION=!RAW_REMOTE: =!

echo Local version:  [%LOCAL_VERSION%]
echo Remote version: [%REMOTE_VERSION%]

:: 4. Comparación de versiones para evitar descargas innecesarias 
if "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
    echo.
    echo ===============================
    echo PKL PIPELINE IS UP TO DATE
    echo ===============================
    echo NO UPDATE IS REQUIRED [cite: 2]
    echo Version: %LOCAL_VERSION%
    pause
    exit /b 0
)

echo.
echo Update required. Downloading files... [cite: 3]
curl -L -o "%ZIP_FILE%" "%REPO_ZIP_URL%" 
if errorlevel 1 goto ERROR

echo Extracting... 
tar -xf "%ZIP_FILE%" -C "%TEMP%" 
if errorlevel 1 goto ERROR

set EXTRACTED_DIR=%TEMP%\%REPO_NAME%-%REPO_BRANCH%

:: --- ELIMINAR __PYCACHE__ ---
echo Cleaning temporary files (__pycache__)...
for /d /r "%EXTRACTED_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d"
)

echo Updating project folders... 
xcopy /E /Y /I "%EXTRACTED_DIR%\config" "%PIPELINE_ROOT%\config" 
xcopy /E /Y /I "%EXTRACTED_DIR%\core"   "%PIPELINE_ROOT%\core" 
xcopy /E /Y /I "%EXTRACTED_DIR%\ui"     "%PIPELINE_ROOT%\ui" 
xcopy /E /Y /I "%EXTRACTED_DIR%\utils"  "%PIPELINE_ROOT%\utils" 

:: --- AUTO-ACTUALIZAR UPDATE.BAT (Opcional) ---
echo Checking for script updates...
:: Usamos un archivo temporal diferente y no verificamos errorlevel aquí para que no falle el script entero
curl -L -s -o "%TEMP%\new_update.tmp" "%REMOTE_BAT_URL%"
if exist "%TEMP%\new_update.tmp" (
    :: Verificar que el archivo no esté vacío (si GitHub devuelve 404, a veces crea un archivo con texto de error)
    findstr /m "@echo" "%TEMP%\new_update.tmp" >nul
    if !errorlevel! == 0 (
        echo New update script found, applying changes...
        move /y "%TEMP%\new_update.tmp" "%CURRENT_BAT%" >nul
    ) else (
        del "%TEMP%\new_update.tmp"
    )
)

:: 5. Guardar versión sin espacios adicionales 
echo %REMOTE_VERSION%>"%LOCAL_VERSION_FILE%"

echo.
echo UPDATE COMPLETED [cite: 4]
pause
exit /b 0

:ERROR
echo.
echo UPDATE FAILED 
pause
exit /b 1
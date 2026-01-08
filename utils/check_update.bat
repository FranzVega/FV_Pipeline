@echo off
setlocal EnableDelayedExpansion

REM ===============================
REM PKL PIPELINE - VERSION CHECKER
REM Solo compara versiones, NO descarga
REM ===============================

REM Configuracion del Repo
set REPO_OWNER=FranzVega
set REPO_NAME=FV_Pipeline
set REPO_BRANCH=main

REM URL de version remota
set REMOTE_VERSION_URL=https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/%REPO_BRANCH%/version.txt

REM Rutas Locales
REM Este bat esta en utils/, entonces parent es pkl_pipeline/
set PIPELINE_ROOT=%~dp0..
set TEMP_REMOTE_VERSION=%TEMP%\pkl_remote_version_check.txt
set LOCAL_VERSION_FILE=%PIPELINE_ROOT%\version.txt
set SIGNAL_FILE=%PIPELINE_ROOT%\.update_available

REM 1. Leer version local y limpiar espacios
if exist "%LOCAL_VERSION_FILE%" (
    set /p RAW_LOCAL=<"%LOCAL_VERSION_FILE%"
    set LOCAL_VERSION=!RAW_LOCAL: =!
) else (
    set LOCAL_VERSION=0.0.0
)

REM 2. Descargar version remota (silencioso con -s)
curl -L -s -o "%TEMP_REMOTE_VERSION%" "%REMOTE_VERSION_URL%" 2>nul
if errorlevel 1 (
    REM Si falla curl, borrar señal y salir silenciosamente
    if exist "%SIGNAL_FILE%" del "%SIGNAL_FILE%" 2>nul
    exit /b 1
)

REM 3. Leer version remota y limpiar espacios
set /p RAW_REMOTE=<"%TEMP_REMOTE_VERSION%"
set REMOTE_VERSION=!RAW_REMOTE: =!

REM 4. Comparar versiones
if "%LOCAL_VERSION%"=="%REMOTE_VERSION%" (
    REM Up to date - Borrar archivo señal si existe
    if exist "%SIGNAL_FILE%" del "%SIGNAL_FILE%" 2>nul
    exit /b 0
) else (
    REM Update disponible - Crear archivo señal
    echo %REMOTE_VERSION% > "%SIGNAL_FILE%"
    exit /b 0
)
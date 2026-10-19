@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Instala Python 3.10 o superior desde python.org, incluyendo el lanzador py.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -m venv .venv
if not exist ".venv\Scripts\python.exe" (
    echo No se pudo crear el entorno de Python.
    pause
    exit /b 1
)
.venv\Scripts\python.exe -c "import pygame" >nul 2>nul
if errorlevel 1 (
    .venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
    if errorlevel 1 (
        echo No se pudo instalar pygame-ce. Comprueba tu conexion a Internet y la version de Python.
        pause
        exit /b 1
    )
)
.venv\Scripts\python.exe main.py
if errorlevel 1 pause

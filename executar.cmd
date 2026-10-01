@echo off
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Python nao foi encontrado neste computador.
  pause
  exit /b 1
)

py -m pip show pyserial >nul 2>&1
if errorlevel 1 (
  echo Instalando a biblioteca pyserial...
  py -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Nao foi possivel instalar a biblioteca pyserial.
    pause
    exit /b 1
  )
)

py app.py


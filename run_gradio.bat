@echo off
title CHATBOT - Gradio
color 0A

echo ================================================
echo   EJECUTANDO app.py (Gradio)
echo ================================================
echo.

:: Verificar si app.py existe
if not exist "app.py" (
    echo ERROR: No se encuentra app.py
    echo Asegurate de estar en la carpeta correcta
    pause
    exit /b 1
)

:: Verificar e instalar requisitos
echo Verificando requisitos...
python -c "import gradio" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando requisitos faltantes...
    pip install gradio transformers torch
    echo.
)

echo Iniciando servidor Gradio...
echo.
python app.py

pause
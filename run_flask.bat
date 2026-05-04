@echo off
title CHATBOT - Flask Multi-Modelo
color 0B

echo ================================================
echo   EJECUTANDO app_flask.py (Flask)
echo ================================================
echo.

:: Verificar si app_flask.py existe
if not exist "app_flask.py" (
    echo ERROR: No se encuentra app_flask.py
    echo Asegurate de estar en la carpeta correcta
    pause
    exit /b 1
)

:: Verificar e instalar requisitos
echo Verificando requisitos...
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando requisitos para Flask...
    pip install flask requests torch transformers python-dotenv huggingface_hub psutil accelerate sentencepiece
    echo.
)

:: Crear carpeta templates si no existe
if not exist "templates" (
    echo Creando carpeta templates...
    mkdir templates
    echo ADVERTENCIA: Necesitas chat_completo.html dentro de templates
    echo.
)

echo Iniciando servidor Flask en http://localhost:5000
echo.
python app_flask.py

pause
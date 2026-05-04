# run_flask.ps1 - Ejecuta app_flask.py (Flask Multi-Modelo)
# Ejecutar: powershell -ExecutionPolicy Bypass -File run_flask.ps1

Write-Host "================================================" -ForegroundColor Magenta
Write-Host "   EJECUTANDO app_flask.py (Flask)" -ForegroundColor Magenta
Write-Host "================================================`n" -ForegroundColor Magenta

# Verificar si app_flask.py existe
if (-not (Test-Path "app_flask.py")) {
    Write-Host "ERROR: No se encuentra app_flask.py" -ForegroundColor Red
    Write-Host "Asegurate de estar en la carpeta correcta" -ForegroundColor Red
    Read-Host "`nPresiona Enter para salir"
    exit 1
}

# Verificar e instalar requisitos
Write-Host "Verificando requisitos..." -ForegroundColor Yellow
$flaskCheck = python -c "import flask" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando requisitos para Flask..." -ForegroundColor Yellow
    pip install flask requests torch transformers python-dotenv huggingface_hub psutil accelerate sentencepiece
    Write-Host ""
}

# Crear carpeta templates si no existe
if (-not (Test-Path "templates")) {
    Write-Host "Creando carpeta templates..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "templates" -Force | Out-Null
    Write-Host "ADVERTENCIA: Necesitas chat_completo.html dentro de templates" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Iniciando servidor Flask en http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
python app_flask.py

Read-Host "`nPresiona Enter para salir"
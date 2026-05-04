# run_gradio.ps1 - Ejecuta app.py (Gradio)
# Ejecutar: powershell -ExecutionPolicy Bypass -File run_gradio.ps1

Write-Host "================================================" -ForegroundColor Green
Write-Host "   EJECUTANDO app.py (Gradio)" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Green

# Verificar si app.py existe
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: No se encuentra app.py" -ForegroundColor Red
    Write-Host "Asegurate de estar en la carpeta correcta" -ForegroundColor Red
    Read-Host "`nPresiona Enter para salir"
    exit 1
}

# Verificar e instalar requisitos
Write-Host "Verificando requisitos..." -ForegroundColor Yellow
$gradioCheck = python -c "import gradio" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando requisitos faltantes..." -ForegroundColor Yellow
    pip install gradio transformers torch
    Write-Host ""
}

Write-Host "Iniciando servidor Gradio..." -ForegroundColor Cyan
Write-Host ""
python app.py

Read-Host "`nPresiona Enter para salir"
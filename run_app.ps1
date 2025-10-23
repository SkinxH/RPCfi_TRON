# RPCfi Flow Simulator Launcher
Write-Host "Starting RPCfi Flow Simulator..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "rpcfi_env")) {
    Write-Host "Virtual environment not found. Please run setup first." -ForegroundColor Red
    Write-Host "Run: python -m venv rpcfi_env" -ForegroundColor Yellow
    Write-Host "Then: .\rpcfi_env\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "Finally: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\rpcfi_env\Scripts\Activate.ps1"

# Start Streamlit application
Write-Host "Starting Streamlit application..." -ForegroundColor Cyan
Write-Host "The application will open in your default web browser." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the application." -ForegroundColor Yellow
Write-Host ""

streamlit run app.py

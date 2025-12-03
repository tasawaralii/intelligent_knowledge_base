param()

if (-Not (Test-Path -Path "backend/venv")) {
    Write-Host "Virtual environment not found. Run .\scripts\setup-backend.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Changing directory to backend..."
Push-Location -Path .\backend

Write-Host "Activating backend virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Starting Uvicorn (reload)..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host "Restoring working directory..."
Pop-Location
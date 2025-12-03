<#
Setup backend development environment (PowerShell)
Usage: .\scripts\setup-backend.ps1
#>

param()

Write-Host "Creating virtual environment in backend/venv..."
python -m venv backend/venv

Write-Host "Activating virtual environment and installing requirements..."
& .\backend\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt

Write-Host "Done. To run the backend: .\scripts\run-backend.ps1"

<#
Setup frontend development environment (PowerShell)
Usage: .\scripts\setup-frontend.ps1
#>

param()

Write-Host "Checking for Node.js..."
if (-Not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found. Please install Node.js 18+ from https://nodejs.org/ before continuing." -ForegroundColor Red
    exit 1
}

Write-Host "Changing directory to frontend..."
Push-Location -Path .\frontend

if (Test-Path package-lock.json) {
    Write-Host "Installing frontend dependencies (npm ci)..."
    npm ci
} else {
    Write-Host "Installing frontend dependencies (npm install)..."
    npm install
}

Write-Host "Dependencies installed. Restoring working directory..."
Pop-Location

Write-Host "Done. To run the frontend: .\scripts\run-frontend.ps1"

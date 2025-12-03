<#
Run the frontend dev server (PowerShell)
Usage: .\scripts\run-frontend.ps1
#>

param()

if (-Not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found. Please install Node.js 18+ from https://nodejs.org/ before continuing." -ForegroundColor Red
    exit 1
}

Write-Host "Changing directory to frontend..."
Push-Location -Path .\frontend

if (-Not (Test-Path -Path "node_modules")) {
    Write-Host "node_modules not found. Run .\scripts\setup-frontend.ps1 first." -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Write-Host "Starting Vite dev server (npm run dev)..."
& npm run dev

Write-Host "Restoring working directory..."
Pop-Location

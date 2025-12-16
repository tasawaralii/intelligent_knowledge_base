<#
Create `backend/.env` from `.env.example` with interactive prompts.
Usage: .\scripts\create-backend-env.ps1
#>

param()

$example = "backend/.env.example"
$target = "backend/.env"

if (-Not (Test-Path $example)) {
    Write-Host "$example not found." -ForegroundColor Red
    exit 1
}

if (Test-Path $target) {
    $overwrite = Read-Host "backend/.env already exists. Overwrite? (y/N)"
    if ($overwrite -notin @('y','Y')) {
        Write-Host "Aborting. Keeping existing backend/.env" -ForegroundColor Yellow
        exit 0
    }
}

$content = Get-Content $example

Write-Host "Creating backend/.env from example. Press Enter to accept defaults shown in [brackets]."

$out = @()
foreach ($line in $content) {
    if ($line -match '^\s*#' -or $line -match '^\s*$') {
        $out += $line
        continue
    }
    if ($line -match '^(\w+)=(.*)$') {
        $key = $matches[1]
        $val = $matches[2]
        $prompt = "$key [$val] :"
        $input = Read-Host $prompt
        if ([string]::IsNullOrWhiteSpace($input)) { $input = $val }
        $out += "${key}=${input}"
    } else {
        $out += $line
    }
}

$out | Set-Content -Path $target -Encoding UTF8
Write-Host "Created $target" -ForegroundColor Green

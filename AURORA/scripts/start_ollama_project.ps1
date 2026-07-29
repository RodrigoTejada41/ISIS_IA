$ErrorActionPreference = "Stop"

$ollamaRoot = "D:\ISIS_IA\ISIS\runtime\ollama"
$modelsRoot = "D:\ISIS_IA\ISIS\models\ollama"
$ollamaExe = Join-Path $ollamaRoot "ollama.exe"

if (-not (Test-Path -LiteralPath $ollamaExe)) {
    throw "Ollama nao encontrado em $ollamaExe"
}

if (-not (Test-Path -LiteralPath $modelsRoot)) {
    throw "Modelos nao encontrados em $modelsRoot"
}

$env:OLLAMA_MODELS = $modelsRoot

$running = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -eq "ollama" -and $_.Path -eq $ollamaExe } |
    Select-Object -First 1

if (-not $running) {
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WorkingDirectory $ollamaRoot -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

& $ollamaExe list

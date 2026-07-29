$ErrorActionPreference = "Stop"

$ollamaExe = "D:\ISIS_IA\ISIS\runtime\ollama\ollama.exe"
$env:OLLAMA_MODELS = "D:\ISIS_IA\ISIS\models\ollama"

[pscustomobject]@{
    OllamaExe = $ollamaExe
    OllamaExeExists = Test-Path -LiteralPath $ollamaExe
    OllamaModels = $env:OLLAMA_MODELS
    OllamaModelsExists = Test-Path -LiteralPath $env:OLLAMA_MODELS
    UserOllamaModels = [Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User")
    OldAppExists = Test-Path -LiteralPath "C:\Users\Rodrigo Tejada\AppData\Local\Programs\Ollama"
    OldDotOllamaExists = Test-Path -LiteralPath "C:\Users\Rodrigo Tejada\.ollama"
    RunningProcesses = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "ollama*" } | Select-Object Id, ProcessName, Path)
}

if (Test-Path -LiteralPath $ollamaExe) {
    & $ollamaExe list
}

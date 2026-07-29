$ErrorActionPreference = "Stop"

$models = Get-Content "D:\ISIS_IA\AURORA\data\external_models.json" | ConvertFrom-Json

foreach ($model in $models) {
    $exists = Test-Path -LiteralPath $model.path
    $bytes = 0
    if ($exists) {
        $item = Get-Item -LiteralPath $model.path
        if ($item.PSIsContainer) {
            $bytes = (Get-ChildItem -LiteralPath $model.path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
        } else {
            $bytes = $item.Length
        }
    }

    [pscustomobject]@{
        Id = $model.id
        Repo = $model.repo
        Path = $model.path
        Exists = $exists
        GB = [math]::Round($bytes / 1GB, 2)
        Runtime = $model.runtime
        Status = $model.status
        Reason = $model.reason
    }
}

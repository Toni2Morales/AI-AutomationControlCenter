param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = $ScriptDir
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Error "No se encuentra el intérprete: $PythonExe"
    exit 1
}

$OldPyPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = $BackendDir
    & $PythonExe -m pytest (Join-Path $BackendDir "tests") @PytestArgs
    exit $LASTEXITCODE
}
finally {
    $env:PYTHONPATH = $OldPyPath
}

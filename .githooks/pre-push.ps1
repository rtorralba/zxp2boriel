Write-Host "Running tests before push..."
python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Push aborted." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Tests passed. Proceeding with push." -ForegroundColor Green
exit 0

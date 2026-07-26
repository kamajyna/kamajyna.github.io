$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "Generating new blog post..." -ForegroundColor Cyan
python scripts/auto_blogger.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "auto_blogger.py 실행 중 오류가 발생했습니다."
    exit $LASTEXITCODE
}

Write-Host "Committing and pushing to GitHub..." -ForegroundColor Cyan
git add _posts/
$DateStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Auto-published post: $DateStr"
git push origin main

Write-Host "Done!" -ForegroundColor Green

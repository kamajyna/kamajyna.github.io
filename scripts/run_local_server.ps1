$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "로컬 Jekyll 서버를 시작합니다..." -ForegroundColor Cyan
Write-Host "http://localhost:4000/ 에 접속하여 디자인을 확인하세요." -ForegroundColor Yellow

bundle exec jekyll serve --livereload

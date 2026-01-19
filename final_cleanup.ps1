# 최종 정리 스크립트

Write-Host "프로젝트 최종 정리 시작..."

# Backend로 이동
Set-Location backend

# docs와 scripts가 파일이면 삭제 후 디렉토리 생성
if (Test-Path "docs" -PathType Leaf) {
    Remove-Item "docs" -Force
    Write-Host "docs 파일 삭제"
}
if (Test-Path "scripts" -PathType Leaf) {
    Remove-Item "scripts" -Force
    Write-Host "scripts 파일 삭제"
}

New-Item -ItemType Directory -Path "docs" -Force | Out-Null
New-Item -ItemType Directory -Path "scripts" -Force | Out-Null

Write-Host "디렉토리 생성 완료"

# Backend 문서 이동 (기존 파일 덮어쓰기)
Write-Host "Backend 문서 이동 중..."
Get-ChildItem -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" } | ForEach-Object {
    $dest = "docs\$($_.Name)"
    if (Test-Path $dest) {
        Remove-Item $dest -Force
    }
    Move-Item -Path $_.FullName -Destination "docs\" -Force
    Write-Host "  이동: $($_.Name)"
}

# Backend 스크립트 이동
Write-Host "Backend 스크립트 이동 중..."

# Python 스크립트
@("init_models.py", "test_chromadb.py", "test_installation.py") | ForEach-Object {
    if (Test-Path $_) {
        Move-Item -Path $_ -Destination "scripts\" -Force -ErrorAction SilentlyContinue
        Write-Host "  이동: $_"
    }
}

# 배치 파일
Get-ChildItem -Filter "*.bat" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  이동: $($_.Name)"
}

# PowerShell 스크립트 (reorganize.ps1만)
if (Test-Path "reorganize.ps1") {
    Move-Item -Path "reorganize.ps1" -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  이동: reorganize.ps1"
}

# 불필요한 폴더 삭제
if (Test-Path "backend\backend") {
    Remove-Item "backend\backend" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "불필요한 폴더 삭제 완료"
}

Set-Location ..

Write-Host ""
Write-Host "정리 완료!"
Write-Host ""
Write-Host "최종 구조 확인:"
Get-ChildItem -Directory | Select-Object Name


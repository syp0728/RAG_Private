# 프로젝트 구조 완전 정리 스크립트

Write-Host "=========================================="
Write-Host "프로젝트 구조 정리 시작"
Write-Host "=========================================="

# 현재 디렉토리를 루트로 설정
$rootDir = Get-Location
Set-Location $rootDir

# 디렉토리 생성
Write-Host ""
Write-Host "[1/6] 디렉토리 생성 중..."
New-Item -ItemType Directory -Force -Path "docs" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\scripts" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\docs" | Out-Null
Write-Host "디렉토리 생성 완료"

# 루트 레벨 문서 이동
Write-Host ""
Write-Host "[2/6] 루트 레벨 문서 정리 중..."
$rootDocs = @("INSTALL.md", "OLLAMA_SETUP.md", "PROJECT_STRUCTURE.md", "QUICKSTART.md", "REORGANIZE.md", "CLEANUP_GUIDE.md")
foreach ($doc in $rootDocs) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination "docs\" -Force -ErrorAction SilentlyContinue
        Write-Host "  이동: $doc"
    }
}
Write-Host "루트 문서 정리 완료"

# 루트 레벨 스크립트 이동
Write-Host ""
Write-Host "[3/6] 루트 레벨 스크립트 정리 중..."
$rootScripts = @("setup.bat", "setup.sh")
foreach ($script in $rootScripts) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination "scripts\" -Force -ErrorAction SilentlyContinue
        Write-Host "  이동: $script"
    }
}
Write-Host "루트 스크립트 정리 완료"

# Backend 문서 이동
Write-Host ""
Write-Host "[4/6] Backend 문서 정리 중..."
Set-Location backend
$backendDocs = Get-ChildItem -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" }
foreach ($doc in $backendDocs) {
    Move-Item -Path $doc.FullName -Destination "docs\" -Force -ErrorAction SilentlyContinue
    Write-Host "  이동: $($doc.Name)"
}
Write-Host "Backend 문서 정리 완료"

# Backend 스크립트 이동
Write-Host ""
Write-Host "[5/6] Backend 스크립트 정리 중..."
# scripts 파일이 있으면 삭제
if (Test-Path "scripts" -PathType Leaf) {
    Remove-Item "scripts" -Force
}
New-Item -ItemType Directory -Path "scripts" -Force | Out-Null

# Python 스크립트 이동
$pythonScripts = @("init_models.py", "test_chromadb.py", "test_installation.py")
foreach ($script in $pythonScripts) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination "scripts\" -Force -ErrorAction SilentlyContinue
        Write-Host "  이동: $script"
    }
}

# 배치 파일 이동
$batFiles = Get-ChildItem -Filter "*.bat" -File
foreach ($bat in $batFiles) {
    Move-Item -Path $bat.FullName -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  이동: $($bat.Name)"
}

# PowerShell 스크립트 이동 (cleanup_project.ps1 제외)
$psFiles = Get-ChildItem -Filter "*.ps1" -File | Where-Object { $_.Name -ne "cleanup_project.ps1" }
foreach ($ps in $psFiles) {
    Move-Item -Path $ps.FullName -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  이동: $($ps.Name)"
}
Write-Host "Backend 스크립트 정리 완료"

# 불필요한 폴더 정리
Write-Host ""
Write-Host "[6/6] 불필요한 폴더 정리 중..."
Set-Location $rootDir
if (Test-Path "backend\backend") {
    Remove-Item "backend\backend" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  삭제: backend\backend"
}
Write-Host "정리 완료"

Write-Host ""
Write-Host "=========================================="
Write-Host "프로젝트 구조 정리 완료!"
Write-Host "=========================================="
Write-Host ""
Write-Host "최종 구조:"
Write-Host "  docs/              - 프로젝트 문서"
Write-Host "  scripts/           - 루트 스크립트"
Write-Host "  backend/docs/      - Backend 문서"
Write-Host "  backend/scripts/   - Backend 스크립트"
Write-Host "  backend/core/      - 핵심 모듈"
Write-Host ""

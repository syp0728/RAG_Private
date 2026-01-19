# 프로젝트 구조 재정리 스크립트

# 디렉토리 생성
New-Item -ItemType Directory -Force -Path "docs" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts" | Out-Null
New-Item -ItemType Directory -Force -Path "core" | Out-Null

# 문서 파일 이동
Move-Item -Path "*.md" -Destination "docs\" -Force -ErrorAction SilentlyContinue

# 배치 파일 이동
Move-Item -Path "*.bat" -Destination "scripts\" -Force -ErrorAction SilentlyContinue

# 테스트 스크립트 이동
Move-Item -Path "test_*.py" -Destination "scripts\" -Force -ErrorAction SilentlyContinue

# 초기화 스크립트 이동
Move-Item -Path "init_models.py" -Destination "scripts\" -Force -ErrorAction SilentlyContinue

# 핵심 모듈 이동
Move-Item -Path "rag_system.py" -Destination "core\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "file_manager.py" -Destination "core\" -Force -ErrorAction SilentlyContinue
Move-Item -Path "document_processor.py" -Destination "core\" -Force -ErrorAction SilentlyContinue

Write-Host "파일 정리 완료!"


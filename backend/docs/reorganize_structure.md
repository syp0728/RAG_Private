# 프로젝트 구조 재정리 가이드

## 수동 정리 방법

다음 명령어를 PowerShell에서 실행하세요:

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend

# 디렉토리 생성
New-Item -ItemType Directory -Force -Path "docs"
New-Item -ItemType Directory -Force -Path "scripts"
New-Item -ItemType Directory -Force -Path "core"

# 문서 파일 이동
Move-Item -Path "*.md" -Destination "docs\" -Force

# 배치 파일 이동
Move-Item -Path "*.bat" -Destination "scripts\" -Force

# 테스트 및 초기화 스크립트 이동
Move-Item -Path "test_*.py" -Destination "scripts\" -Force
Move-Item -Path "init_models.py" -Destination "scripts\" -Force

# 핵심 모듈 이동
Move-Item -Path "rag_system.py" -Destination "core\" -Force
Move-Item -Path "file_manager.py" -Destination "core\" -Force
Move-Item -Path "document_processor.py" -Destination "core\" -Force
```

## 이동 후 import 수정

파일 이동 후 다음 파일들의 import를 수정해야 합니다:

1. `backend/app.py`: 
   ```python
   from core.rag_system import RAGSystem
   from core.file_manager import FileManager
   ```

2. `backend/core/rag_system.py`:
   ```python
   from .document_processor import DocumentProcessor
   ```

3. `backend/scripts/init_models.py`:
   ```python
   import sys
   sys.path.insert(0, '..')
   from config import *
   ```

## 최종 구조

```
backend/
├── core/              # 핵심 비즈니스 로직
│   ├── __init__.py
│   ├── rag_system.py
│   ├── document_processor.py
│   └── file_manager.py
├── scripts/          # 유틸리티 스크립트
│   ├── init_models.py
│   ├── test_*.py
│   └── install_*.bat
├── docs/             # 문서
│   └── *.md
├── app.py           # Flask 서버 진입점
├── config.py        # 설정
└── requirements.txt
```


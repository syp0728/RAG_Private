# 프로젝트 구조 재정리 가이드

## 현재 상태
파일들이 backend 폴더에 평면적으로 배치되어 있습니다.

## 목표 구조

```
RAG_Private/
├── backend/
│   ├── core/              # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── rag_system.py
│   │   ├── document_processor.py
│   │   └── file_manager.py
│   ├── scripts/          # 유틸리티 스크립트
│   │   ├── init_models.py
│   │   ├── test_chromadb.py
│   │   ├── test_installation.py
│   │   └── install_*.bat
│   ├── docs/             # Backend 문서
│   │   ├── INSTALL_WINDOWS.md
│   │   ├── START_GUIDE.md
│   │   └── ...
│   ├── app.py            # Flask 서버 진입점
│   ├── config.py         # 설정
│   └── requirements.txt
├── frontend/             # Frontend (변경 없음)
├── docs/                 # 프로젝트 문서
│   ├── INSTALL.md
│   ├── OLLAMA_SETUP.md
│   └── ...
└── scripts/              # 루트 스크립트
    ├── setup.bat
    └── setup.sh
```

## 정리 방법

### 방법 1: PowerShell 스크립트 실행 (권장)

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
.\reorganize.ps1
```

### 방법 2: 수동 정리

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

## 이동 후 수정 사항

### 1. backend/app.py 수정

```python
from config import *
from core.rag_system import RAGSystem
from core.file_manager import FileManager
```

### 2. backend/core/rag_system.py 수정

```python
from config import *
from .document_processor import DocumentProcessor
```

### 3. backend/core/__init__.py 생성 (이미 생성됨)

### 4. backend/scripts/init_models.py 수정

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import *
```

## 루트 레벨 정리

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private

# 루트 문서 이동
New-Item -ItemType Directory -Force -Path "docs"
Move-Item -Path "*.md" -Destination "docs\" -Force -Exclude "README.md"

# 루트 스크립트 이동
New-Item -ItemType Directory -Force -Path "scripts"
Move-Item -Path "*.bat" -Destination "scripts\" -Force
Move-Item -Path "*.sh" -Destination "scripts\" -Force
```

## 확인

정리 후 다음 명령어로 확인:

```powershell
# Backend 구조 확인
tree backend /F

# 전체 구조 확인
tree /F /A
```

## 주의사항

- 파일 이동 후 import 경로를 반드시 수정해야 합니다
- `venv311` 폴더는 이동하지 마세요
- `__pycache__` 폴더는 자동 생성되므로 무시해도 됩니다


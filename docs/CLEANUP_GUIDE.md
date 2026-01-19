# 프로젝트 구조 정리 가이드

## 자동 정리 스크립트 실행

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private
.\cleanup_project.ps1
```

## 정리 후 구조

```
RAG_Private/
├── README.md                    # 프로젝트 개요 (간단)
├── .gitignore                   # Git 제외 파일
├── docker-compose.yml          # Docker Compose 설정
│
├── docs/                        # 📚 프로젝트 문서
│   ├── README.md               # 상세 문서
│   ├── INSTALL.md              # 설치 가이드
│   ├── OLLAMA_SETUP.md         # Ollama 설정
│   ├── PROJECT_STRUCTURE.md    # 프로젝트 구조
│   ├── QUICKSTART.md           # 빠른 시작
│   └── REORGANIZE.md           # 구조 정리 가이드
│
├── scripts/                     # 🔧 루트 스크립트
│   ├── setup.bat               # Windows 설치
│   └── setup.sh                # Linux 설치
│
├── backend/                     # 🐍 Backend 서버
│   ├── core/                   # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── rag_system.py       # RAG 엔진
│   │   ├── document_processor.py  # 문서 처리
│   │   └── file_manager.py     # 파일 관리
│   │
│   ├── scripts/                # Backend 스크립트
│   │   ├── init_models.py      # 모델 초기화
│   │   ├── test_chromadb.py    # ChromaDB 테스트
│   │   ├── test_installation.py # 설치 테스트
│   │   ├── install_*.bat        # 설치 스크립트
│   │   └── reorganize.ps1      # 구조 정리
│   │
│   ├── docs/                   # Backend 문서
│   │   ├── INSTALL_WINDOWS.md
│   │   ├── START_GUIDE.md
│   │   └── ...
│   │
│   ├── app.py                  # Flask 서버 진입점
│   ├── config.py               # 설정 파일
│   ├── requirements.txt        # Python 의존성
│   └── Dockerfile              # Docker 이미지
│
├── frontend/                    # ⚛️ Frontend 애플리케이션
│   ├── src/
│   │   ├── components/         # React 컴포넌트
│   │   ├── services/           # API 클라이언트
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── data/                       # 💾 런타임 데이터 (자동 생성)
│   ├── uploads/                # 업로드된 파일
│   └── chroma_db/              # ChromaDB 저장소
│
└── models/                     # 🤖 모델 가중치 (자동 생성)
    └── sentence-transformers/  # 임베딩 모델 캐시
```

## 정리 항목

### ✅ 루트 레벨
- 모든 `.md` 파일 → `docs/`
- 모든 `.bat`, `.sh` 파일 → `scripts/`
- `README.md`는 루트에 유지 (간단 버전)

### ✅ Backend 레벨
- 핵심 모듈 → `backend/core/`
- 모든 스크립트 → `backend/scripts/`
- 모든 문서 → `backend/docs/`
- 불필요한 `backend/backend/` 폴더 삭제

## 정리 후 확인

```powershell
# 구조 확인
tree /F /A

# 또는
Get-ChildItem -Recurse -Directory | Select-Object FullName
```

## 주의사항

- `venv311/` 폴더는 이동하지 않습니다
- `data/`, `models/` 폴더는 그대로 유지합니다
- `__pycache__/` 폴더는 자동 생성되므로 무시해도 됩니다


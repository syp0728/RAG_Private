# 최종 프로젝트 구조

## 정리 완료된 구조

```
RAG_Private/
├── README.md                    # 프로젝트 개요
├── .gitignore                   # Git 제외 파일
├── docker-compose.yml          # Docker Compose 설정
├── cleanup_project.ps1         # 구조 정리 스크립트
│
├── docs/                        # 📚 프로젝트 문서
│   ├── README.md               # 상세 문서
│   ├── INSTALL.md              # 설치 가이드
│   ├── OLLAMA_SETUP.md         # Ollama 설정
│   ├── PROJECT_STRUCTURE.md    # 프로젝트 구조
│   ├── QUICKSTART.md           # 빠른 시작
│   ├── REORGANIZE.md           # 구조 정리 가이드
│   └── CLEANUP_GUIDE.md        # 정리 가이드
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
│   │   ├── install_*.bat       # 설치 스크립트
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

## 정리 상태

- ✅ 루트 레벨 문서 → `docs/`
- ✅ 루트 레벨 스크립트 → `scripts/`
- ✅ Backend 핵심 모듈 → `backend/core/`
- ✅ Backend 스크립트 → `backend/scripts/`
- ✅ Backend 문서 → `backend/docs/`

## 다음 단계

정리가 완료되면:
1. `backend/app.py`의 import 경로 확인
2. `backend/scripts/init_models.py`의 경로 수정 확인
3. 테스트 실행


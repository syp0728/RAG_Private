# 프로젝트 구조

## 전체 구조

```
RAG_Private/
├── backend/                 # Backend 서버
│   ├── core/               # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── rag_system.py      # RAG 엔진 (하이브리드 자원 분배)
│   │   ├── document_processor.py  # Layout-aware 문서 처리
│   │   └── file_manager.py    # 파일 관리
│   ├── scripts/            # 유틸리티 스크립트
│   │   ├── init_models.py     # 모델 초기화
│   │   ├── test_*.py         # 테스트 스크립트
│   │   └── install_*.bat      # 설치 스크립트
│   ├── docs/              # Backend 관련 문서
│   │   ├── INSTALL_WINDOWS.md
│   │   ├── START_GUIDE.md
│   │   └── ...
│   ├── app.py             # Flask API 서버 (진입점)
│   ├── config.py          # 설정 파일
│   ├── requirements.txt   # Python 의존성
│   └── Dockerfile         # Docker 이미지 설정
│
├── frontend/              # Frontend 애플리케이션
│   ├── src/
│   │   ├── components/   # React 컴포넌트
│   │   │   ├── ChatInterface.jsx
│   │   │   └── FileManager.jsx
│   │   ├── services/     # API 클라이언트
│   │   │   └── api.js
│   │   ├── App.jsx        # 메인 앱 컴포넌트
│   │   └── main.jsx       # 진입점
│   ├── package.json       # Node.js 의존성
│   ├── vite.config.js     # Vite 설정
│   └── Dockerfile         # Docker 이미지 설정
│
├── docs/                  # 프로젝트 문서
│   ├── INSTALL.md         # 설치 가이드
│   ├── OLLAMA_SETUP.md    # Ollama 설정 가이드
│   └── ...
│
├── scripts/               # 루트 레벨 스크립트
│   ├── setup.bat          # Windows 설치 스크립트
│   └── setup.sh           # Linux 설치 스크립트
│
├── data/                  # 데이터 저장소 (생성됨)
│   ├── uploads/           # 업로드된 원본 파일
│   └── chroma_db/         # ChromaDB 벡터 저장소
│
├── models/                # 모델 가중치 (생성됨)
│   └── sentence-transformers/  # 임베딩 모델
│
├── docker-compose.yml     # Docker Compose 설정
├── README.md              # 프로젝트 개요
└── .gitignore            # Git 제외 파일
```

## 디렉토리 설명

### backend/
Backend 서버 코드

- **core/**: 핵심 비즈니스 로직
  - `rag_system.py`: RAG 엔진 (하이브리드 자원 분배, ChromaDB 통합)
  - `document_processor.py`: Layout-aware 문서 처리 (표/이미지 지원)
  - `file_manager.py`: 파일 업로드/다운로드 관리

- **scripts/**: 유틸리티 스크립트
  - `init_models.py`: 임베딩 모델 초기화
  - `test_*.py`: 테스트 스크립트
  - `install_*.bat`: Windows 설치 스크립트

- **docs/**: Backend 관련 문서
  - 설치 가이드, 문제 해결 가이드 등

- **app.py**: Flask API 서버 진입점
- **config.py**: 전역 설정 (경로, 모델, DB 등)

### frontend/
Frontend React 애플리케이션

- **src/components/**: UI 컴포넌트
  - `ChatInterface.jsx`: 채팅 인터페이스
  - `FileManager.jsx`: 파일 관리 UI

- **src/services/**: API 통신
  - `api.js`: Axios 기반 API 클라이언트

### docs/
프로젝트 전체 문서

- 설치 가이드, 설정 가이드, 문제 해결 가이드 등

### scripts/
루트 레벨 설치/배포 스크립트

### data/
런타임 데이터 저장소 (자동 생성)

- `uploads/`: 업로드된 원본 파일
- `chroma_db/`: ChromaDB 벡터 저장소

### models/
로컬 모델 가중치 (자동 생성)

- `sentence-transformers/`: 임베딩 모델 캐시

## 주요 파일

### Backend
- `backend/app.py`: Flask API 서버 메인 파일
- `backend/config.py`: 전역 설정
- `backend/core/rag_system.py`: RAG 시스템 핵심 로직

### Frontend
- `frontend/src/App.jsx`: React 앱 메인 컴포넌트
- `frontend/src/components/ChatInterface.jsx`: 채팅 UI

### 설정
- `docker-compose.yml`: 전체 시스템 Docker 배포 설정
- `backend/requirements.txt`: Python 의존성
- `frontend/package.json`: Node.js 의존성

## 실행 흐름

1. **Backend 시작**: `backend/app.py` 실행
   - `config.py`에서 설정 로드
   - `core/rag_system.py`에서 RAG 시스템 초기화
   - Flask API 서버 시작 (포트 5000)

2. **Frontend 시작**: `frontend/src/main.jsx` 실행
   - React 앱 렌더링
   - `services/api.js`를 통해 Backend와 통신

3. **사용자 요청 흐름**:
   - Frontend → API 요청 → Backend `app.py`
   - → `core/rag_system.py` → ChromaDB 검색
   - → Ollama LLM → 응답 반환


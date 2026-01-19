# Private RAG AI Agent - 온프레미스 기반 기업용 RAG 시스템

## 개요
사내 문서 유출을 원천 차단한 온프레미스 기반 RAG(Retrieval-Augmented Generation) 시스템입니다.

## 기술 스택
- **Frontend**: React + Vite
- **Backend**: Python (LangChain)
- **LLM**: Ollama (llama3.1:8b-instruct-q4_K_M)
- **Vector DB**: ChromaDB
- **Embedding**: bge-m3 (CPU 실행)
- **하드웨어 요구사항**: NVIDIA RTX 4060 (8GB VRAM) / 32GB RAM

## 주요 기능
- ✅ 하이브리드 자원 분배 (임베딩: CPU, LLM: GPU)
- ✅ Layout-aware 문서 처리 (표/이미지 지원)
- ✅ 100% 오프라인 동작
- ✅ 파일 업로드/다운로드 관리
- ✅ 소스 참조 및 페이지 번호 표시
- ✅ 할루시네이션 방지

## 빠른 시작

### 1. 설치
```bash
# Backend
cd backend
python -m venv venv311
venv311\Scripts\activate  # Windows
pip install -r requirements.txt
python scripts/init_models.py

# Frontend
cd frontend
npm install
```

### 2. 실행
```bash
# Ollama 서버 (별도 터미널)
ollama serve
ollama pull llama3.1:8b-instruct-q4_K_M

# Backend (별도 터미널)
cd backend
venv311\Scripts\activate
python app.py

# Frontend (별도 터미널)
cd frontend
npm run dev
```

## 프로젝트 구조

```
RAG_Private/
├── backend/              # Backend 서버
│   ├── core/            # 핵심 비즈니스 로직
│   ├── scripts/         # 유틸리티 스크립트
│   ├── docs/            # Backend 문서
│   ├── app.py           # Flask 서버 진입점
│   └── config.py        # 설정
├── frontend/            # Frontend 애플리케이션
├── docs/                # 프로젝트 문서
├── scripts/             # 루트 스크립트
├── data/                # 런타임 데이터
└── models/              # 모델 가중치
```

자세한 구조는 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 참조

## 문서

- [설치 가이드](INSTALL.md)
- [Ollama 설정](OLLAMA_SETUP.md)
- [프로젝트 구조](PROJECT_STRUCTURE.md)
- [빠른 시작](QUICKSTART.md)

## 라이선스

기업 내부 사용 전용


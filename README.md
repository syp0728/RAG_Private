# Private RAG AI Agent

온프레미스 기반 기업용 RAG(Retrieval-Augmented Generation) 시스템

## 빠른 시작

### 초기 설정 (처음 한 번만)

#### 1. Ollama 설치 및 모델 다운로드
```powershell
# Ollama 다운로드: https://ollama.ai/download
# 설치 후 모델 다운로드
ollama pull llama3.1:8b-instruct-q4_K_M
```

#### 2. Backend 설정
```powershell
# 프로젝트 디렉토리로 이동
cd C:\Users\SSPLUS\Documents\RAG_Private

# Backend 디렉토리로 이동
cd backend

# 가상환경 생성 (처음 한 번만)
python -m venv venv311

# 가상환경 활성화
.\venv311\Scripts\Activate.ps1

# 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 임베딩 모델 다운로드 (처음 한 번만)
python scripts/init_models.py
```

#### 3. Frontend 설정
```powershell
# 프로젝트 루트 디렉토리로 이동
cd C:\Users\SSPLUS\Documents\RAG_Private

# Frontend 디렉토리로 이동
cd frontend

# 의존성 설치 (처음 한 번만)
npm install
```

### 실행 방법 (매번 실행 시)

**중요**: 다음 순서대로 실행해야 합니다.

#### 1단계: Ollama 서버 실행
새 PowerShell 터미널을 열고:
```powershell
ollama serve
```
**주의**: 이 터미널을 닫지 마세요! Ollama 서버가 계속 실행되어야 합니다.

#### 2단계: Backend 서버 실행
새 PowerShell 터미널을 열고:
```powershell
# 프로젝트 디렉토리로 이동
cd C:\Users\SSPLUS\Documents\RAG_Private\backend

# 가상환경 활성화
.\venv311\Scripts\Activate.ps1

# Backend 서버 실행
python app.py
```
Backend는 `http://localhost:5000`에서 실행됩니다.

#### 3단계: Frontend 실행
새 PowerShell 터미널을 열고:
```powershell
# 프로젝트 디렉토리로 이동
cd C:\Users\SSPLUS\Documents\RAG_Private\frontend

# Frontend 실행
npm run dev
```
Frontend는 `http://localhost:3000` (또는 다른 포트)에서 실행됩니다.

### 실행 확인

1. 브라우저에서 `http://localhost:3000` 접속
2. 상단에 "백엔드 연결됨" 표시 확인
3. 파일 관리 탭에서 파일 업로드 테스트
4. 채팅 탭에서 질문 테스트

### 종료 방법

각 터미널에서 `Ctrl + C`를 눌러 종료합니다.

## 문서

- 📖 [전체 문서](docs/README.md)
- 🚀 [빠른 시작 가이드](docs/QUICKSTART.md)
- 📦 [설치 가이드](docs/INSTALL.md)
- ⚙️ [Ollama 설정](docs/OLLAMA_SETUP.md)
- 📁 [프로젝트 구조](docs/PROJECT_STRUCTURE.md)

## 주요 기능

- ✅ 하이브리드 자원 분배 (임베딩: CPU, LLM: GPU)
- ✅ Layout-aware 문서 처리
- ✅ 100% 오프라인 동작
- ✅ 할루시네이션 방지

## 기술 스택

- Frontend: React + Vite
- Backend: Python Flask + LangChain
- LLM: Ollama (llama3.1:8b-instruct-q4_K_M)
- Vector DB: ChromaDB
- Embedding: bge-m3 (CPU)

---

자세한 내용은 [docs/README.md](docs/README.md)를 참조하세요.

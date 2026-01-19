# Private RAG 시스템 설치 가이드

## 사전 요구사항

### 하드웨어
- NVIDIA GeForce RTX 4060 (8GB VRAM) 이상
- 32GB RAM 이상
- 충분한 디스크 공간 (모델 저장용)

### 소프트웨어
- Python 3.11 이상
- Node.js 18 이상
- Ollama (최신 버전)
- CUDA Toolkit (GPU 사용 시)

## 설치 단계

### 1. Ollama 설치 및 모델 다운로드

#### Windows
```bash
# Ollama 다운로드: https://ollama.ai/download
# 설치 후 실행
ollama serve

# 모델 다운로드 (별도 터미널)
ollama pull llama3.1:8b-instruct-q4_K_M
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# 모델 다운로드 (별도 터미널)
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 2. Backend 설정

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 모델 초기화 (임베딩 모델 다운로드)
python init_models.py
```

### 3. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install
```

### 4. 실행

#### Backend 실행
```bash
cd backend
python app.py
```
Backend는 `http://localhost:5000`에서 실행됩니다.

#### Frontend 실행
```bash
cd frontend
npm run dev
```
Frontend는 `http://localhost:3000`에서 실행됩니다.

#### Ollama 실행
```bash
ollama serve
```
Ollama는 `http://localhost:11434`에서 실행됩니다.

## Docker로 실행 (권장)

### Docker Compose 사용

```bash
# 전체 시스템 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

**주의**: GPU 사용을 위해서는 Docker에서 NVIDIA Container Toolkit이 설치되어 있어야 합니다.

## 문제 해결

### Ollama 연결 오류
- Ollama가 실행 중인지 확인: `ollama list`
- 환경 변수 `OLLAMA_BASE_URL` 확인

### GPU 메모리 부족
- `backend/config.py`에서 `EMBEDDING_DEVICE = "cpu"` 확인
- Ollama 모델을 더 작은 버전으로 변경 (예: `llama3.1:8b-instruct-q4_K_M` → `llama3.1:8b-instruct-q4_K_S`)

### 모델 다운로드 실패
- 인터넷 연결 확인 (초기 다운로드만 필요)
- HuggingFace 토큰 설정 (필요시)

## 오프라인 모드

모델을 한 번 다운로드한 후에는:
- 임베딩 모델: `models/sentence-transformers/` 디렉토리에 저장
- Ollama 모델: `~/.ollama/` 디렉토리에 저장

이 디렉토리를 백업하면 오프라인에서도 사용 가능합니다.


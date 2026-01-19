# 빠른 시작 가이드

## 현재 문제 해결

현재 `C:\Users\SSPLUS\Documents\RAG\backend`에서 실행 중이시지만, 프로젝트는 `C:\Users\SSPLUS\Documents\RAG_Private`에 있습니다.

## 올바른 실행 방법

### 1. 프로젝트 디렉토리로 이동

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
```

### 2. 가상 환경 활성화 (이미 활성화되어 있다면 생략)

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. 의존성 설치

```powershell
pip install -r requirements.txt
```

### 4. 모델 초기화

```powershell
python init_models.py
```

## 임베딩 CPU 실행 확인

임베딩 모델은 **반드시 CPU에서 실행**되도록 설정되어 있습니다:

- ✅ `backend/config.py`: `EMBEDDING_DEVICE = "cpu"` (고정)
- ✅ `backend/rag_system.py`: `device=EMBEDDING_DEVICE` 사용

이 설정으로 인해:
- **임베딩(bge-m3)**: CPU에서 실행 → GPU 메모리 절약
- **Ollama LLM**: GPU에서 실행 → 빠른 추론

RTX 4060의 8GB VRAM을 효율적으로 사용할 수 있습니다.


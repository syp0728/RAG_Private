# 설치 완료 확인

## 현재 상태

패키지 설치가 완료되었습니다! 이제 시스템을 테스트해보세요.

## 중요: Python 버전 확인

현재 Python 3.11 가상환경을 사용하고 있는지 확인하세요:

```powershell
# Python 버전 확인
python --version
# Python 3.11.x가 나와야 합니다!

# 만약 Python 3.14가 나오면:
deactivate
venv311\Scripts\activate
python --version
```

## 설치 확인

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
python test_installation.py
```

## 다음 단계

### 1. 모델 다운로드

```powershell
python init_models.py
```

### 2. Ollama 설정

```powershell
# 터미널 1: Ollama 실행
ollama serve

# 터미널 2: 모델 다운로드
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 3. 서버 실행

```powershell
python app.py
```

## 문제 해결

### ChromaDB 오류가 나는 경우
- Python 3.11 가상환경이 활성화되어 있는지 확인
- `python --version`으로 버전 확인

### 모델 다운로드 실패
- 인터넷 연결 확인
- HuggingFace 토큰 필요 시 설정


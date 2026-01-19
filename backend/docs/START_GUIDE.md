# 시작 가이드

## 설치 완료! ✅

모든 패키지가 성공적으로 설치되었습니다.

## 다음 단계

### 1. 모델 초기화 (임베딩 모델 다운로드)

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
python init_models.py
```

이 명령어는:
- 임베딩 모델 (bge-m3)을 CPU용으로 다운로드합니다
- 모델은 `models/` 디렉토리에 저장됩니다

### 2. Ollama 모델 다운로드

별도 터미널에서 Ollama를 실행하고 모델을 다운로드하세요:

```powershell
# Ollama 실행 (별도 터미널)
ollama serve

# 다른 터미널에서 모델 다운로드
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 3. Backend 서버 실행

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

### 4. Frontend 실행 (별도 터미널)

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\frontend
npm install
npm run dev
```

Frontend는 `http://localhost:3000`에서 실행됩니다.

## 시스템 테스트

### ChromaDB 테스트
```powershell
python test_chromadb.py
```

### 전체 시스템 테스트
```powershell
python app.py
# 브라우저에서 http://localhost:5000/api/health 접속
```

## 문제 해결

### Ollama 연결 오류
- Ollama가 실행 중인지 확인: `ollama list`
- 환경 변수 확인: `OLLAMA_BASE_URL=http://localhost:11434`

### 모델 다운로드 실패
- 인터넷 연결 확인
- HuggingFace 토큰 필요 시 설정

## 완료!

이제 Private RAG 시스템을 사용할 수 있습니다! 🎉


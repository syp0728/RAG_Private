# Ollama 설정 가이드

## Ollama는 가상환경과 무관합니다

Ollama는 **시스템 레벨 서비스**이므로 Python 가상환경과는 별개로 작동합니다.

## 설치 및 실행 방법

### 1. Ollama 설치 (시스템 레벨)

Ollama가 설치되어 있지 않다면:
- Windows: https://ollama.ai/download 에서 다운로드 및 설치
- 설치 후 자동으로 시스템 서비스로 등록됩니다

### 2. Ollama 서버 실행 (시스템 레벨)

**가상환경 활성화 없이** 일반 PowerShell/CMD에서:

```powershell
# 가상환경 비활성화 상태에서 실행
ollama serve
```

또는 Windows에서는 Ollama가 자동으로 백그라운드에서 실행될 수 있습니다.

### 3. 모델 다운로드 (시스템 레벨)

**가상환경 활성화 없이** 별도 터미널에서:

```powershell
# 가상환경 비활성화 상태에서 실행
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 4. 모델 확인

```powershell
# 설치된 모델 목록 확인
ollama list
```

## 전체 실행 순서

### 터미널 1: Ollama 서버 (가상환경 불필요)
```powershell
# 가상환경 비활성화 상태
ollama serve
```

### 터미널 2: 모델 다운로드 (가상환경 불필요)
```powershell
# 가상환경 비활성화 상태
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 터미널 3: Backend 서버 (가상환경 필요)
```powershell
# 가상환경 활성화
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
venv311\Scripts\activate
python app.py
```

### 터미널 4: Frontend (가상환경 불필요)
```powershell
# 가상환경 비활성화 상태
cd C:\Users\SSPLUS\Documents\RAG_Private\frontend
npm run dev
```

## 요약

- ✅ **Ollama 실행/모델 다운로드**: 가상환경 **불필요** (시스템 레벨)
- ✅ **Backend Python 서버**: 가상환경 **필요** (venv311)
- ✅ **Frontend**: 가상환경 **불필요** (Node.js)

## 모델 저장 위치

Ollama 모델은 다음 위치에 저장됩니다:
- Windows: `C:\Users\<사용자명>\.ollama\models\`
- 이 위치는 시스템 전역에서 접근 가능합니다

## 확인 방법

```powershell
# Ollama가 실행 중인지 확인
ollama list

# 특정 모델이 있는지 확인
ollama show llama3.1:8b-instruct-q4_K_M
```


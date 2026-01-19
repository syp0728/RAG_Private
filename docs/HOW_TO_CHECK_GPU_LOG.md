# Ollama GPU 사용 확인 방법

## 방법 1: Ollama 실행 로그 확인 (가장 확실함)

### 1단계: Ollama가 실행 중인지 확인

```powershell
# 새로운 PowerShell 터미널을 열고
ollama list
```

모델 목록이 나오면 Ollama가 실행 중입니다.

### 2단계: Ollama 서버 재시작하여 로그 확인

Ollama 서버를 시작/재시작하면 시작 로그에 GPU 정보가 나타납니다:

```powershell
# Ollama 종료 (Ctrl+C로 중지)
# 그 다음 다시 시작
ollama serve
```

**로그에서 찾아야 할 내용:**

✅ **GPU 사용 중인 경우:**
```
INFO[0000] loading model                             model=llama3.1:8b-instruct-q4_K_M
INFO[0000] GPU layers: 35                            <- 이 메시지가 중요!
```

❌ **CPU만 사용 중인 경우:**
```
INFO[0000] loading model                             model=llama3.1:8b-instruct-q4_K_M
(GPU layers 메시지가 없음)
```

## 방법 2: 모델 로드 시 로그 확인

모델을 처음 실행하거나 재로드할 때 로그 확인:

```powershell
ollama run llama3.1:8b-instruct-q4_K_M
```

이 명령어 실행 시 모델 로딩 메시지가 나오는데, 여기에 GPU layers 정보가 포함됩니다.

## 방법 3: API로 확인 (스크립트 사용)

```powershell
cd backend
.\venv311\Scripts\Activate.ps1
python scripts/check_ollama_gpu.py
```

현재 응답 시간을 측정하여 GPU 사용 여부를 추정합니다.

## 방법 4: 추론 중 GPU 사용량 실시간 모니터링

**두 개의 터미널 필요:**

**터미널 1:** 추론 실행
```powershell
# RAG 시스템에서 질문을 보내거나
ollama run llama3.1:8b-instruct-q4_K_M
```

**터미널 2:** GPU 모니터링 (1초마다 갱신)
```powershell
nvidia-smi -l 1
```

질문 처리 중에:
- **GPU-Util**이 50-100%로 증가 → GPU 사용 중 ✅
- **Memory-Usage**가 증가 → GPU 사용 중 ✅
- GPU-Util이 0% 또는 매우 낮음 → CPU만 사용 중 ❌

## 현재 확인된 정보

- **응답 시간**: 3.48초
- **GPU 하드웨어**: RTX 4060 (8GB) ✅ 감지됨
- **GPU 사용 여부**: 확인 필요 (Ollama 로그 확인 필요)

## 다음 단계

1. Ollama 서버를 재시작하고 로그에서 "GPU layers" 메시지 확인
2. 또는 추론 중 `nvidia-smi -l 1`로 GPU 사용량 모니터링


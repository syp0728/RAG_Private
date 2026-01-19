# GPU 인식 문제 해결 단계별 가이드

## 현재 상황 확인

✅ **환경 변수**: `CUDA_VISIBLE_DEVICES` 설정 없음 (정상)
✅ **GPU 하드웨어**: RTX 4060 감지됨
❌ **Ollama GPU 인식**: 실패 (CPU만 사용)

## 해결 단계

### 1단계: Ollama 완전 종료

현재 `ollama serve`가 실행 중인 터미널에서:
- **Ctrl + C**로 종료
- 터미널 창 닫기

### 2단계: Ollama 재시작

**새로운 PowerShell 터미널**을 열고:

```powershell
ollama serve
```

### 3단계: 로그 확인

시작 시 로그에서 다음을 확인:

#### ✅ GPU 인식 성공 시:
```
level=INFO msg="inference compute" id=0 library=cuda compute="8.9" name="NVIDIA GeForce RTX 4060"
"total vram"="8188 MiB"  <- 0 B가 아닌 값
```

또는 모델 로드 시:
```
GPU layers: 35
```

#### ❌ GPU 인식 실패 시 (현재 상태):
```
level=INFO msg="inference compute" id=cpu library=cpu
"total vram"="0 B"  <- 여전히 0 B
```

### 4단계: 모델 로드 테스트

Ollama 서버가 실행 중인 상태에서 **다른 터미널**을 열어:

```powershell
ollama run llama3.1:8b-instruct-q4_K_M
```

모델이 로드될 때 로그에서:
- `GPU layers: X` 메시지 확인

### 5단계: 성능 테스트

GPU가 인식되면:

```powershell
cd C:\Users\SSPLUS\Documents\RAG_Private\backend
.\venv311\Scripts\Activate.ps1
python scripts/check_ollama_gpu.py
```

응답 시간이 **1-2초**로 단축되면 GPU 사용 중입니다.

## 여전히 GPU가 인식되지 않으면

### 방법 1: Ollama 재설치

1. Ollama 완전 제거
2. https://ollama.ai/download 에서 최신 버전 다운로드
3. 재설치
4. 재시작

### 방법 2: CUDA Toolkit 확인

Windows에서 Ollama는 자동으로 CUDA를 감지합니다. 하지만 다음과 같이 확인:

```powershell
# CUDA 경로 확인 (보통 자동)
$env:PATH | Select-String -Pattern "CUDA"
```

### 방법 3: 관리자 권한으로 실행

때로는 관리자 권한이 필요할 수 있습니다:

```powershell
# PowerShell을 관리자 권한으로 실행
ollama serve
```

## 성공 확인 방법

GPU가 정상 작동하면:

1. **로그에서**: `library=cuda` 또는 `GPU layers: X`
2. **성능**: 응답 시간 1-2초 (현재 3.48초 → CPU 사용 중)
3. **nvidia-smi**: 추론 중 GPU-Util 증가

## 참고

- Windows에서 Ollama GPU 인식은 때때로 지연될 수 있습니다
- 재시작 후에도 동일하면 재설치를 권장합니다
- Ollama 0.13.5 버전에서는 GPU 자동 감지가 개선되었습니다


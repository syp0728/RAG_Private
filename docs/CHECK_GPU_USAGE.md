# GPU 사용 확인 방법

## 현재 상태

테스트 결과:
- **응답 시간**: 3.48초
- **GPU 사용 여부**: 중간 (GPU 사용 가능성 있지만 최적화 필요)

## 확실한 확인 방법

### 1. Ollama 로그 확인 (가장 확실함)

Ollama를 실행할 때 다음 명령어로 로그 확인:

```powershell
ollama serve
```

**GPU를 사용 중이면:**
```
time=2026-01-19T09:00:00.000Z level=INFO msg="loading model" model=llama3.1:8b-instruct-q4_K_M
time=2026-01-19T09:00:00.100Z level=INFO msg="GPU layers: 35"  # <- 이 메시지 확인!
```

**CPU만 사용 중이면:**
```
time=2026-01-19T09:00:00.000Z level=INFO msg="loading model" model=llama3.1:8b-instruct-q4_K_M
# GPU layers 메시지가 없음
```

### 2. 추론 중 GPU 사용량 모니터링

추론 중에 GPU 사용량 확인:

```powershell
# 첫 번째 터미널: Ollama 실행
ollama serve

# 두 번째 터미널: 추론 실행
ollama run llama3.1:8b-instruct-q4_K_M

# 세 번째 터미널: GPU 모니터링 (추론 중에 실행)
nvidia-smi -l 1
```

**GPU 사용 중이면:**
- GPU-Util이 50-100%로 증가
- Memory-Usage가 증가 (모델 크기에 따라 2-6GB)
- Compute processes에 ollama.exe 또는 ollama 관련 프로세스 표시

### 3. 성능 기준

| 응답 시간 | GPU 사용 가능성 |
|----------|---------------|
| 1초 이하 | 매우 빠름 (GPU 사용 중) |
| 1-3초 | 빠름 (GPU 사용 중) |
| 3-5초 | 보통 (GPU 사용 중이거나 제한적) |
| 5초 이상 | 느림 (CPU만 사용 가능성) |

현재 **3.48초**는 GPU를 사용하고 있지만 최적화가 필요한 상태입니다.

## GPU 사용 문제 해결

### Windows에서 GPU 인식 안 되는 경우

1. **NVIDIA 드라이버 확인**
   ```powershell
   nvidia-smi
   ```
   최신 드라이버 설치: https://www.nvidia.com/drivers

2. **Ollama 재설치**
   - Ollama 완전 제거 후 재설치
   - 재설치 시 GPU 자동 감지

3. **CUDA 확인**
   ```powershell
   nvidia-smi
   # CUDA Version: 12.6 이상 확인
   ```

### 성능 최적화

1. **더 작은 모델 사용**
   ```powershell
   ollama pull llama3.1:8b-instruct-q4_K_S
   ```
   `backend/config.py`에서:
   ```python
   OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_S"
   ```

2. **num_predict 줄이기** (이미 적용됨)
   - 현재: `num_predict: 1000`
   - 더 빠르게: `num_predict: 500`

## 참고

- Ollama는 자동으로 GPU를 감지합니다
- GPU가 감지되면 자동으로 GPU layers를 사용합니다
- GPU layers 수는 모델과 GPU 메모리에 따라 자동 조정됩니다
- RTX 4060 (8GB)의 경우 일반적으로 30-35 layers를 GPU에서 실행합니다


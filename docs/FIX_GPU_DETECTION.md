# Ollama GPU 인식 문제 해결

## 현재 상태

Ollama 로그에서 확인:
- ❌ `library=cpu` → CPU만 사용 중
- ❌ `"total vram"="0 B"` → GPU가 감지되지 않음

## 해결 방법

### 1. NVIDIA 드라이버 확인

```powershell
nvidia-smi
```

**확인 사항:**
- GPU가 감지되는가? (RTX 4060 표시되어야 함)
- 드라이버 버전이 최신인가?
- CUDA Version이 표시되는가?

### 2. CUDA 및 cuDNN 확인

Ollama는 CUDA를 자동으로 감지합니다. 다음 확인:

1. **NVIDIA 드라이버 최신 버전 설치**
   - https://www.nvidia.com/drivers 에서 최신 드라이버 다운로드

2. **Windows 환경 변수 확인**
   ```powershell
   $env:CUDA_VISIBLE_DEVICES
   # 비어있어야 함 (설정되어 있으면 제거)
   ```

### 3. Ollama 재시작

1. Ollama 완전 종료 (Ctrl+C)
2. 다시 시작:
   ```powershell
   ollama serve
   ```
3. 로그에서 다시 확인:
   - `library=cuda` 또는 `library=hip` 또는 GPU 관련 메시지 확인
   - `"total vram"`이 0이 아닌 값으로 표시되어야 함

### 4. Ollama 재설치 (최후의 수단)

만약 위 방법들이 작동하지 않으면:

1. Ollama 완전 제거
2. https://ollama.ai/download 에서 최신 버전 다운로드
3. 재설치
4. 재시작

### 5. 모델 재다운로드

재설치 후:

```powershell
ollama pull llama3.1:8b-instruct-q4_K_M
```

## 성공 시 로그 모습

GPU가 정상적으로 인식되면:

```
level=INFO msg="inference compute" id=0 library=cuda compute="8.9" name="NVIDIA GeForce RTX 4060"
"total vram"="8188 MiB"
```

또는

```
level=INFO msg="GPU layers: 35"
```

## 현재 상황 요약

- **하드웨어**: RTX 4060 (8GB) ✅ 감지됨
- **Ollama GPU 인식**: ❌ 실패 (CPU만 사용)
- **응답 시간**: 3.48초 (CPU 사용 중)

GPU가 인식되면 응답 시간이 **1-2초**로 단축될 것입니다.


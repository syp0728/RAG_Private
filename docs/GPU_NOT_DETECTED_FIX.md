# Ollama GPU 인식 실패 해결 방법

## 현재 상태

- ✅ GPU 하드웨어: RTX 4060 정상 감지 (nvidia-smi)
- ✅ NVIDIA 드라이버: 560.94 정상
- ✅ CUDA Version: 12.6
- ❌ Ollama GPU 인식: 실패 (CPU만 사용)
- ❌ Ollama 버전: 0.13.5

## 해결 방법 (순서대로 시도)

### 방법 1: Ollama 재설치 (가장 효과적)

1. **Ollama 완전 종료**
   - 모든 Ollama 프로세스 종료
   - 작업 관리자에서 `ollama.exe` 확인 후 종료

2. **Ollama 제거**
   - Windows 설정 → 앱 → Ollama 제거

3. **최신 버전 다운로드 및 재설치**
   - https://ollama.ai/download
   - Windows용 최신 버전 다운로드
   - 재설치

4. **관리자 권한으로 실행**
   ```powershell
   # PowerShell을 관리자 권한으로 실행
   ollama serve
   ```

### 방법 2: Ollama 서비스 확인

Ollama가 Windows 서비스로 실행되고 있는지 확인:

```powershell
Get-Service | Where-Object {$_.Name -like "*ollama*"}
```

서비스가 있다면:
```powershell
# 서비스 중지
Stop-Service -Name "Ollama" -Force

# 수동으로 실행
ollama serve
```

### 방법 3: CUDA 경로 확인

Ollama가 CUDA를 찾을 수 있는지 확인:

```powershell
# CUDA 관련 환경 변수 확인
$env:PATH | Select-String -Pattern "CUDA"

# NVIDIA 드라이버 경로 확인
Test-Path "C:\Windows\System32\nvcuda.dll"
```

### 방법 4: Ollama 실행 파일 위치 확인

```powershell
# Ollama 실행 파일 확인
Get-Command ollama | Select-Object Source

# 실행 파일에서 직접 실행
& "C:\Users\SSPLUS\AppData\Local\Programs\Ollama\ollama.exe" serve
```

### 방법 5: Windows 재부팅

가끔 Windows 재부팅으로 GPU 인식 문제가 해결됩니다.

## 확인 방법

재시작 후 로그에서 확인:

**✅ 성공:**
```
library=cuda compute="8.9" name="NVIDIA GeForce RTX 4060"
"total vram"="8188 MiB"
```

**❌ 실패 (현재):**
```
library=cpu
"total vram"="0 B"
```

## 모델 실행으로 확인

다른 터미널에서:
```powershell
ollama run llama3.1:8b-instruct-q4_K_M
```

성공 시 모델 로드 로그에 `GPU layers: X` 메시지가 나타납니다.

## 참고사항

- Ollama 0.13.5는 Windows에서 GPU 자동 감지가 개선되었습니다
- 하지만 일부 환경에서는 여전히 문제가 발생할 수 있습니다
- 재설치는 가장 확실한 해결 방법입니다

## 성능 차이

- **CPU 사용 중 (현재)**: 3-5초 응답 시간
- **GPU 사용 시**: 1-2초 응답 시간

GPU 인식 문제가 해결되면 성능이 크게 개선됩니다.


# Ollama 포트 사용 중 오류 해결

## 오류 메시지
```
Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted.
```

이것은 포트 11434가 이미 사용 중이라는 의미입니다.

## 해결 방법

### 방법 1: Ollama 프로세스 종료

```powershell
# Ollama 프로세스 찾기
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

# 모든 Ollama 프로세스 종료
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"} | Stop-Process -Force
```

### 방법 2: 포트를 사용하는 프로세스 확인 및 종료

```powershell
# 포트 11434를 사용하는 프로세스 찾기
$processId = (Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue).OwningProcess

if ($processId) {
    # 프로세스 정보 확인
    Get-Process -Id $processId | Select-Object ProcessName, Id, Path
    
    # 프로세스 종료
    Stop-Process -Id $processId -Force
    Write-Host "프로세스 종료 완료"
} else {
    Write-Host "포트를 사용하는 프로세스를 찾을 수 없습니다"
}
```

### 방법 3: Windows 서비스 확인

Ollama가 Windows 서비스로 실행 중일 수 있습니다:

```powershell
# Ollama 서비스 확인
Get-Service | Where-Object {$_.Name -like "*ollama*"}

# 서비스가 있다면 중지
Stop-Service -Name "Ollama" -Force -ErrorAction SilentlyContinue
```

### 방법 4: 작업 관리자에서 수동 종료

1. Ctrl + Shift + Esc로 작업 관리자 열기
2. "세부 정보" 탭에서 `ollama.exe` 찾기
3. 선택 후 "작업 끝내기"

### 방법 5: 재부팅 (가장 확실한 방법)

위 방법들이 작동하지 않으면 Windows를 재부팅하세요.

## 확인

프로세스를 종료한 후:

```powershell
# 포트가 비어있는지 확인
Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue

# 아무것도 나오지 않으면 포트가 비어있습니다
```

그 다음 Ollama 재시작:

```powershell
ollama serve
```

## 성공 확인

Ollama가 정상적으로 시작되면 로그가 표시됩니다. GPU 인식 여부도 다시 확인하세요:

✅ **GPU 인식 성공:**
```
library=cuda
"total vram"="8188 MiB"
```

❌ **GPU 인식 실패 (현재):**
```
library=cpu
"total vram"="0 B"
```


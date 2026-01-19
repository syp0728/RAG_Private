# Windows 설치 가이드

## ChromaDB onnxruntime 오류 해결

Windows에서 ChromaDB 설치 시 `onnxruntime>=1.14.1` 오류가 발생할 수 있습니다.

### 해결 방법 1: 자동 설치 스크립트 사용 (권장)

```powershell
cd backend
.\install_windows_fix.bat
```

### 해결 방법 2: 수동 설치

```powershell
# 1. pip 업그레이드
python -m pip install --upgrade pip setuptools wheel

# 2. onnxruntime 먼저 설치 (CPU 버전)
python -m pip install onnxruntime>=1.15.0

# 3. 나머지 패키지 설치
python -m pip install -r requirements.txt
```

### 해결 방법 3: onnxruntime 버전 명시

```powershell
# 특정 버전으로 설치
python -m pip install onnxruntime==1.15.1
python -m pip install chromadb==0.4.22
```

### Visual C++ Runtime 필요 시

Windows에서 onnxruntime을 사용하려면 Visual C++ 2019 Runtime이 필요할 수 있습니다:
- [Visual C++ 2019 재배포 가능 패키지](https://aka.ms/vs/17/release/vc_redist.x64.exe) 다운로드 및 설치

## Pillow 설치 오류 해결

Windows에서 Pillow 설치 시 빌드 오류가 발생할 수 있습니다. 다음 순서로 설치하세요:

### 1. pip, setuptools, wheel 업그레이드

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 2. Pillow를 먼저 설치 (사전 빌드된 wheel 사용)

```powershell
pip install pillow
```

또는 특정 버전:

```powershell
pip install pillow>=10.0.0
```

### 3. 나머지 패키지 설치

```powershell
pip install -r requirements.txt
```

## 대안: Pillow 없이 설치 (이미지 처리 제외)

이미지 처리가 필요 없다면, Pillow를 제외하고 설치할 수 있습니다:

```powershell
pip install flask flask-cors chromadb sentence-transformers ollama pypdf2 python-docx python-multipart werkzeug
```

## Visual C++ 빌드 도구 설치 (소스 빌드 필요 시)

Pillow를 소스에서 빌드해야 하는 경우:

1. [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) 다운로드
2. "C++ 빌드 도구" 워크로드 설치
3. 다시 설치 시도


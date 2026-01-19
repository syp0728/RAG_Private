# Python 3.14 호환성 문제 해결

## 문제
Python 3.14.0을 사용 중이며, `onnxruntime`은 Python 3.11까지만 지원합니다.

## 해결 방법

### 방법 1: ChromaDB 의존성 우회 (권장)

```powershell
# 자동 설치 스크립트 사용
.\install_python314.bat
```

또는 수동 설치:

```powershell
# 1. pip 업그레이드
python -m pip install --upgrade pip setuptools wheel

# 2. ChromaDB 설치 (의존성 제외)
python -m pip install chromadb==0.4.15 --no-deps

# 3. ChromaDB 필수 의존성만 설치
python -m pip install httpx uvicorn posthog pypika overrides typing-extensions

# 4. 나머지 패키지 설치
python -m pip install -r requirements.txt
```

### 방법 2: Python 3.11로 다운그레이드 (가장 확실)

Python 3.11을 별도로 설치하고 가상환경을 다시 만드세요:

```powershell
# Python 3.11 설치 (python.org에서 다운로드)
# 그 다음:
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 방법 3: ChromaDB 없이 FAISS 사용

ChromaDB 대신 FAISS를 사용하는 방법도 있습니다 (코드 수정 필요).

## 현재 상태

- ✅ ChromaDB 0.4.15는 onnxruntime을 선택적 의존성으로 처리
- ⚠️ 일부 ChromaDB 고급 기능이 제한될 수 있음
- ✅ 기본 RAG 기능은 정상 작동

## 확인

설치 후 테스트:

```powershell
python -c "import chromadb; print('ChromaDB 설치 성공!')"
```


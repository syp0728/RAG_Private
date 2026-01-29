# 🚀 Private RAG 시스템 설치 가이드

> Windows 환경에서 처음부터 끝까지 따라하면 완성되는 설치 매뉴얼

---

## 📋 목차

1. [사전 준비](#1-사전-준비)
2. [필수 소프트웨어 설치](#2-필수-소프트웨어-설치)
3. [프로젝트 다운로드](#3-프로젝트-다운로드)
4. [백엔드 설정](#4-백엔드-설정)
5. [프론트엔드 설정](#5-프론트엔드-설정)
6. [AI 모델 설정](#6-ai-모델-설정)
7. [실행 및 테스트](#7-실행-및-테스트)
8. [문제 해결](#8-문제-해결)

---

## 1. 사전 준비

### 시스템 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| OS | Windows 10 (64bit) | Windows 11 |
| RAM | 16GB | 32GB |
| 저장공간 | 20GB 여유 | 50GB 이상 SSD |
| GPU | - | NVIDIA RTX 4060+ (VRAM 8GB+) |
| 인터넷 | 초기 설치 시 필요 | 이후 오프라인 가능 |

### 설치할 소프트웨어 목록

| 소프트웨어 | 버전 | 용도 |
|-----------|------|------|
| Python | 3.11.x | 백엔드 서버 |
| Node.js | 18.x 이상 | 프론트엔드 빌드 |
| Ollama | 최신 | 로컬 LLM 서버 |
| Git | 최신 (선택) | 프로젝트 다운로드 |

---

## 2. 필수 소프트웨어 설치

### 2.1 Python 3.11 설치

> ⚠️ **중요**: Python 3.12 이상은 일부 라이브러리와 호환성 문제가 있습니다. 반드시 **3.11.x** 버전을 설치하세요.

**방법 1: 공식 홈페이지**
1. https://www.python.org/downloads/release/python-3119/ 접속
2. 하단 "Files"에서 `Windows installer (64-bit)` 다운로드
3. 설치 시 **"Add Python to PATH"** 체크 필수!
4. "Install Now" 클릭

**방법 2: Microsoft Store**
1. Microsoft Store 실행
2. "Python 3.11" 검색
3. "Python 3.11" 설치 (Python Software Foundation)

**설치 확인**:
```powershell
# PowerShell 실행 후
python --version
# 출력: Python 3.11.x

pip --version
# 출력: pip 23.x.x from ...
```

---

### 2.2 Node.js 설치

1. https://nodejs.org/ 접속
2. **LTS** 버전 다운로드 (예: 20.x.x LTS)
3. 설치 프로그램 실행
4. 모든 옵션 기본값으로 "Next" 클릭
5. "Automatically install necessary tools" 체크 권장

**설치 확인**:
```powershell
node --version
# 출력: v20.x.x

npm --version
# 출력: 10.x.x
```

---

### 2.3 Ollama 설치 (로컬 LLM 서버)

1. https://ollama.com/download 접속
2. "Download for Windows" 클릭
3. `OllamaSetup.exe` 실행
4. 설치 완료 후 자동 시작됨

**설치 확인**:
```powershell
ollama --version
# 출력: ollama version 0.x.x
```

---

### 2.4 Git 설치 (선택사항)

> 프로젝트를 ZIP으로 다운로드할 경우 Git 설치는 필요 없습니다.

1. https://git-scm.com/download/win 접속
2. "64-bit Git for Windows Setup" 다운로드
3. 모든 옵션 기본값으로 설치

**설치 확인**:
```powershell
git --version
# 출력: git version 2.x.x
```

---

### 2.5 (선택) NVIDIA GPU 드라이버

> GPU가 있으면 LLM 응답 속도가 5-10배 빨라집니다.

1. https://www.nvidia.com/drivers 접속
2. 본인 GPU 모델 선택 후 드라이버 다운로드
3. 설치 후 재부팅

**GPU 확인**:
```powershell
nvidia-smi
# GPU 정보와 VRAM 사용량이 표시되면 성공
```

---

## 3. 프로젝트 다운로드

### 방법 1: Git Clone (Git 설치 시)

```powershell
# 원하는 폴더로 이동 (예: Documents)
cd C:\Users\사용자이름\Documents

# 프로젝트 복제
git clone https://github.com/your-repo/RAG_Private.git

# 프로젝트 폴더로 이동
cd RAG_Private
```

### 방법 2: ZIP 다운로드 (Git 없이)

1. GitHub 저장소 페이지에서 "Code" → "Download ZIP" 클릭
2. 다운로드된 ZIP 파일을 원하는 위치에 압축 해제
3. 압축 해제된 폴더 이름을 `RAG_Private`으로 변경

---

## 4. 백엔드 설정

### 4.1 폴더 이동 및 가상환경 생성

```powershell
# 프로젝트 폴더로 이동
cd C:\Users\사용자이름\Documents\RAG_Private

# 백엔드 폴더로 이동
cd backend

# Python 가상환경 생성
python -m venv venv311

# 가상환경 활성화
.\venv311\Scripts\Activate.ps1
```

> 💡 **Tip**: 가상환경이 활성화되면 프롬프트 앞에 `(venv311)`이 표시됩니다.

**PowerShell 스크립트 실행 오류 시**:
```powershell
# 관리자 권한으로 PowerShell 실행 후
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 4.2 Python 패키지 설치

```powershell
# 가상환경이 활성화된 상태에서
pip install --upgrade pip

# 모든 의존성 설치 (약 5-10분 소요)
pip install -r requirements.txt
```

**설치되는 주요 패키지**:
| 패키지 | 용도 |
|--------|------|
| flask | 웹 API 서버 |
| chromadb | 벡터 데이터베이스 |
| sentence-transformers | 문서 임베딩 |
| pdfplumber | PDF 표 추출 |
| easyocr | 이미지 OCR |
| opencv-python-headless | 표 선 감지 |

---

### 4.3 데이터 폴더 생성

```powershell
# 프로젝트 루트로 이동
cd ..

# 필요한 폴더 생성
mkdir data
mkdir data\uploads
mkdir data\chroma_db
mkdir models
```

최종 폴더 구조:
```
RAG_Private/
├── backend/
├── frontend/
├── data/
│   ├── uploads/     ← 업로드된 파일 저장
│   └── chroma_db/   ← 벡터 DB 저장
├── models/          ← 임베딩 모델 캐시
└── docs/
```

---

## 5. 프론트엔드 설정

### 5.1 Node.js 패키지 설치

```powershell
# 프론트엔드 폴더로 이동
cd frontend

# 패키지 설치 (약 2-3분 소요)
npm install
```

---

## 6. AI 모델 설정

### 6.1 LLM 모델 다운로드

```powershell
# Ollama로 llama3.1 8B 모델 다운로드 (약 4.7GB)
ollama pull llama3.1:8b-instruct-q4_K_M
```

> ⏱️ 인터넷 속도에 따라 10-30분 소요

**다운로드 확인**:
```powershell
ollama list
# NAME                              SIZE
# llama3.1:8b-instruct-q4_K_M      4.7 GB
```

### 6.2 (선택) 임베딩 모델 사전 다운로드

> 첫 실행 시 자동 다운로드되지만, 미리 받아두면 빠릅니다.

```powershell
cd backend
.\venv311\Scripts\Activate.ps1

python -c "from sentence_transformers import SentenceTransformer; print('Downloading...'); SentenceTransformer('BAAI/bge-m3'); print('Done!')"
```

> ⏱️ 약 2.2GB, 5-15분 소요

---

## 7. 실행 및 테스트

### 7.1 백엔드 서버 실행

**터미널 1** (PowerShell):
```powershell
cd C:\Users\사용자이름\Documents\RAG_Private\backend

# 가상환경 활성화
.\venv311\Scripts\Activate.ps1

# 서버 실행
python -u app.py
```

**정상 실행 시 출력**:
```
=== RAG System 초기화 ===
ChromaDB 연결...
임베딩 모델 로딩: BAAI/bge-m3
Ollama 모델: llama3.1:8b-instruct-q4_K_M
Reranker 모델 로딩...
=== 초기화 완료 ===
 * Running on http://127.0.0.1:5000
```

### 7.2 프론트엔드 서버 실행

**터미널 2** (새 PowerShell 창):
```powershell
cd C:\Users\사용자이름\Documents\RAG_Private\frontend

# 개발 서버 실행
npm run dev
```

**정상 실행 시 출력**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### 7.3 웹 브라우저에서 접속

1. 브라우저를 열고 `http://localhost:5173` 접속
2. "파일 관리" 탭에서 PDF/DOCX/Excel 파일 업로드
3. "채팅" 탭에서 질문 입력
4. AI 답변 확인!

---

## 8. 문제 해결

### 8.1 자주 발생하는 오류

| 오류 | 원인 | 해결 방법 |
|------|------|----------|
| `python is not recognized` | Python PATH 미설정 | Python 재설치 (Add to PATH 체크) |
| `npm is not recognized` | Node.js PATH 미설정 | Node.js 재설치 또는 PC 재시작 |
| `ollama: command not found` | Ollama 미설치 | Ollama 재설치 또는 PC 재시작 |
| `Address already in use` | 포트 충돌 | `taskkill /F /IM python.exe` 후 재시작 |
| `Failed to send telemetry` | ChromaDB 내부 버그 | 무시 가능 (기능에 영향 없음) |

### 8.2 PowerShell 스크립트 실행 오류

```powershell
# 오류: "이 시스템에서 스크립트를 실행할 수 없습니다"
# 해결:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8.3 GPU가 인식되지 않을 때

```powershell
# Ollama가 CPU 모드로 실행 중인지 확인
$env:OLLAMA_DEBUG=1
ollama run llama3.1:8b-instruct-q4_K_M "test"

# 출력에 "CUDA" 또는 "GPU"가 없으면 CPU 모드
# 해결: NVIDIA 드라이버 업데이트 후 Ollama 재설치
```

### 8.4 임베딩 모델 다운로드 실패

```powershell
# 수동 다운로드
pip install huggingface_hub
huggingface-cli download BAAI/bge-m3

# 또는 캐시 삭제 후 재시도
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\huggingface
```

### 8.5 ChromaDB 오류

```powershell
# DB 초기화 (모든 데이터 삭제)
Remove-Item -Recurse -Force ..\data\chroma_db\*

# 백엔드 재시작 후 파일 다시 업로드
```

---

## 🎉 설치 완료!

모든 설정이 완료되었습니다. 이제 사내 문서를 업로드하고 AI에게 질문해보세요!

### 다음 단계

1. **문서 업로드**: PDF, DOCX, Excel 파일 업로드
2. **질문하기**: "이 문서의 핵심 내용은?" 등 질문
3. **파일명 규칙**: `YYMMDD_문서유형_제목.pdf` 형식 권장 (메타데이터 자동 추출)

### 추가 문서

- [기술 명세서](./TECHNICAL_SPEC.md) - 상세 아키텍처
- [파이프라인 설명](./PIPELINE.md) - 처리 흐름
- [README](../README.md) - 빠른 시작 가이드

---

*Last Updated: 2026-01-29*


@echo off
REM Windows용 ChromaDB 설치 스크립트 (onnxruntime 문제 해결)

echo ==========================================
echo ChromaDB 설치 (Windows 호환성 수정)
echo ==========================================

echo.
echo [1/4] pip, setuptools, wheel 업그레이드...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [2/4] onnxruntime 설치 (CPU 버전)...
python -m pip install onnxruntime>=1.15.0

if %errorlevel% neq 0 (
    echo.
    echo 경고: onnxruntime 설치 실패. CPU 버전으로 재시도...
    python -m pip install onnxruntime==1.15.1 --no-deps
)

echo.
echo [3/4] 나머지 필수 패키지 설치...
python -m pip install flask==3.0.0 flask-cors==4.0.0 pypdf2==3.0.1 python-docx==1.1.0 python-multipart==0.0.6 werkzeug==3.0.1

echo.
echo [4/4] ChromaDB 및 기타 패키지 설치...
python -m pip install chromadb==0.4.22 sentence-transformers==2.3.1 ollama==0.1.7 langchain==0.1.0 langchain-community==0.0.10

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo ✅ 설치 완료!
) else (
    echo ❌ 일부 패키지 설치 실패
)
echo ==========================================
pause


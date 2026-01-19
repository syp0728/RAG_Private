@echo off
REM Python 3.14용 ChromaDB 설치 스크립트 (onnxruntime 우회)

echo ==========================================
echo Python 3.14용 패키지 설치
echo ==========================================

echo.
echo [주의] Python 3.14는 onnxruntime을 지원하지 않습니다.
echo ChromaDB 0.4.15 버전을 사용하여 onnxruntime 의존성을 우회합니다.
echo.

echo [1/3] pip 업그레이드...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [2/3] ChromaDB 설치 (onnxruntime 의존성 제외)...
python -m pip install chromadb==0.4.15 --no-deps

echo.
echo [3/4] ChromaDB 필수 의존성 설치...
python -m pip install httpx uvicorn posthog pypika overrides typing-extensions bcrypt chroma-hnswlib fastapi grpcio importlib-resources opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk typer

echo.
echo [4/5] 나머지 필수 패키지 설치...
python -m pip install flask==3.0.0 flask-cors==4.0.0 sentence-transformers==2.3.1 ollama==0.1.7 pypdf2==3.0.1 python-docx==1.1.0 python-multipart==0.0.6 werkzeug==3.0.1 langchain==0.1.0 langchain-community==0.0.10

echo.
echo ==========================================
if %errorlevel% equ 0 (
    echo ✅ 설치 완료!
echo.
echo 참고: ChromaDB는 onnxruntime 없이 작동하지만,
echo 일부 고급 기능이 제한될 수 있습니다.
echo.
echo 누락된 의존성 설치 중...
python -m pip install bcrypt chroma-hnswlib fastapi grpcio importlib-resources opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk typer
) else (
    echo ❌ 일부 패키지 설치 실패
)
echo ==========================================
pause


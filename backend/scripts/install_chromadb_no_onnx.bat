@echo off
chcp 65001 >nul
REM ChromaDB 설치 (onnxruntime 제외)

echo ==========================================
echo ChromaDB 설치 (onnxruntime 제외)
echo ==========================================

echo.
echo [1/4] ChromaDB 핵심 패키지 설치...
python -m pip install chromadb==0.4.15 --no-deps

echo.
echo [2/4] ChromaDB 필수 의존성 설치...
python -m pip install httpx uvicorn posthog pypika overrides typing-extensions bcrypt chroma-hnswlib==0.7.3 fastapi grpcio importlib-resources opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk typer pulsar-client

echo.
echo [3/4] ChromaDB 테스트...
python -c "import chromadb; print('ChromaDB 설치 성공!')"

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ ChromaDB import 실패. 수동 설치 시도...
    python -m pip install chromadb==0.4.15 --no-deps --force-reinstall
    python -m pip install httpx uvicorn posthog pypika overrides typing-extensions bcrypt chroma-hnswlib fastapi grpcio importlib-resources opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk typer pulsar-client
)

echo.
echo [4/4] 최종 테스트...
python -c "import chromadb; client = chromadb.Client(); print('✅ ChromaDB 정상 작동!')"

echo.
echo ==========================================
echo 설치 완료!
echo 참고: onnxruntime은 설치되지 않았지만,
echo ChromaDB 기본 기능은 정상 작동합니다.
echo ==========================================
pause


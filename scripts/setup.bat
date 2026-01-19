@echo off
REM Private RAG 시스템 초기 설정 스크립트 (Windows)

echo ==========================================
echo Private RAG - 초기 설정
echo ==========================================

REM 디렉토리 생성
echo 디렉토리 생성 중...
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\chroma_db" mkdir "data\chroma_db"
if not exist "models" mkdir "models"

REM Backend 의존성 설치
echo Backend 의존성 설치 중...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

REM Frontend 의존성 설치
echo Frontend 의존성 설치 중...
cd frontend
call npm install
cd ..

REM 모델 초기화
echo 모델 다운로드 중...
cd backend
python init_models.py
cd ..

echo.
echo ==========================================
echo 설정 완료!
echo ==========================================
echo.
echo 실행 방법:
echo   Backend:  cd backend ^&^& python app.py
echo   Frontend: cd frontend ^&^& npm run dev
echo   Ollama:   ollama serve (별도 터미널)
echo.
pause


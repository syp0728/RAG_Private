@echo off
chcp 65001 >nul
REM Python 3.11 설치 가이드

echo ==========================================
echo Python 3.11 가상환경 설정
echo ==========================================

echo.
echo [1/3] Python 3.11 버전 확인...
py -3.11 --version

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python 3.11이 설치되지 않았습니다.
    echo Python 3.11을 먼저 설치하세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/3] 가상환경 생성...
py -3.11 -m venv venv311

echo.
echo [3/3] 가상환경 활성화 및 패키지 설치...
call venv311\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==========================================
echo 설치 완료!
echo.
echo 가상환경 활성화:
echo   venv311\Scripts\activate
echo ==========================================
pause


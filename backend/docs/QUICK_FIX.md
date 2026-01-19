# 빠른 해결 방법

## 문제
`requirements.txt` 파일의 한글 주석으로 인한 인코딩 오류

## 해결 완료
- ✅ `requirements.txt` 파일 수정 완료 (한글 주석 제거)
- ✅ ChromaDB 버전을 0.4.22로 설정 (Python 3.11 호환)

## 다음 단계

### 1. Python 3.11 가상환경에서 설치

```powershell
# 현재 가상환경이 Python 3.11인지 확인
python --version
# Python 3.11.x가 나와야 합니다

# 만약 Python 3.14가 나오면:
# 1. 가상환경 비활성화
deactivate

# 2. Python 3.11 가상환경 활성화
venv311\Scripts\activate

# 3. Python 버전 확인
python --version

# 4. 패키지 설치
pip install -r requirements.txt
```

### 2. 또는 자동 스크립트 사용

```powershell
.\install_python311.bat
```

## 참고
- Python 3.11이 설치되어 있어야 합니다
- Python 3.11 다운로드: https://www.python.org/downloads/release/python-3110/


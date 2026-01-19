#!/bin/bash
# Private RAG 시스템 초기 설정 스크립트

set -e

echo "=========================================="
echo "Private RAG - 초기 설정"
echo "=========================================="

# 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p data/uploads
mkdir -p data/chroma_db
mkdir -p models

# Backend 의존성 설치
echo "📦 Backend 의존성 설치 중..."
cd backend
python -m venv venv || python3 -m venv venv
source venv/bin/activate || source venv/Scripts/activate  # Windows
pip install -r requirements.txt
cd ..

# Frontend 의존성 설치
echo "📦 Frontend 의존성 설치 중..."
cd frontend
npm install
cd ..

# 모델 초기화
echo "🤖 모델 다운로드 중..."
cd backend
python init_models.py
cd ..

# Ollama 모델 확인
echo ""
echo "⚠️  Ollama 모델 다운로드:"
echo "   ollama pull llama3.1:8b-instruct-q4_K_M"

echo ""
echo "=========================================="
echo "✅ 설정 완료!"
echo "=========================================="
echo ""
echo "실행 방법:"
echo "  Backend:  cd backend && python app.py"
echo "  Frontend: cd frontend && npm run dev"
echo "  Ollama:   ollama serve (별도 터미널)"


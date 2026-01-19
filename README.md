# Private RAG AI Agent

온프레미스 기반 기업용 RAG(Retrieval-Augmented Generation) 시스템

## 빠른 시작

```bash
# 1. Backend 설정
cd backend
python -m venv venv311
venv311\Scripts\activate
pip install -r requirements.txt
python scripts/init_models.py

# 2. Ollama 모델 다운로드
ollama pull llama3.1:8b-instruct-q4_K_M

# 3. 실행
python app.py  # Backend
npm run dev    # Frontend (별도 터미널)
```

## 문서

- 📖 [전체 문서](docs/README.md)
- 🚀 [빠른 시작 가이드](docs/QUICKSTART.md)
- 📦 [설치 가이드](docs/INSTALL.md)
- ⚙️ [Ollama 설정](docs/OLLAMA_SETUP.md)
- 📁 [프로젝트 구조](docs/PROJECT_STRUCTURE.md)

## 주요 기능

- ✅ 하이브리드 자원 분배 (임베딩: CPU, LLM: GPU)
- ✅ Layout-aware 문서 처리
- ✅ 100% 오프라인 동작
- ✅ 할루시네이션 방지

## 기술 스택

- Frontend: React + Vite
- Backend: Python Flask + LangChain
- LLM: Ollama (llama3.1:8b-instruct-q4_K_M)
- Vector DB: ChromaDB
- Embedding: bge-m3 (CPU)

---

자세한 내용은 [docs/README.md](docs/README.md)를 참조하세요.

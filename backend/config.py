import os
from pathlib import Path

# 기본 디렉토리 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_DB_DIR = DATA_DIR / "chroma_db"

# 디렉토리 생성
for dir_path in [DATA_DIR, MODELS_DIR, UPLOAD_DIR, VECTOR_DB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Ollama 설정
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_M"

# 임베딩 설정 (CPU에서 실행)
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DEVICE = "cpu"  # CPU로 고정

# ChromaDB 설정
CHROMA_COLLECTION_NAME = "enterprise_documents"
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR)

# 파일 업로드 설정
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

# RAG 설정
TOP_K_RESULTS = 20
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


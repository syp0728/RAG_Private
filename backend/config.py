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
ALLOWED_EXTENSIONS = {
    # 문서 형식
    ".pdf", ".docx", ".txt", ".md", ".xlsx", ".xls",
    # 이미지 형식 (OCR 지원)
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"
}

# RAG 설정
TOP_K_RESULTS = 40           # 검색 결과 수 (상향)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 컨텍스트 구성 설정
MAX_CHUNKS_PER_FILE = 15     # 파일당 최대 유지 청크 수
MIN_CONTEXT_COUNT = 15       # LLM에 전달할 최소 컨텍스트 수
MAX_CONTEXT_COUNT = 30       # LLM에 전달할 최대 컨텍스트 수

# 하이브리드 검색 설정
# [실험적] 고유명사(이름 등) 검색 정확도 향상을 위해 BM25 비중 상향
VECTOR_WEIGHT = 0.4  # 벡터(의미) 검색 가중치
BM25_WEIGHT = 0.6    # BM25(키워드) 검색 가중치

# 재순위화 설정
RERANK_TOP_K = 25    # 재순위화 후 LLM에 전달할 최대 청크 수 (상향)
RERANK_ENABLED = True  # 재순위화 활성화 여부

# Semantic Metadata Tagging (엔티티 추출) 설정
ENTITY_EXTRACTION_ENABLED = True  # 인덱싱 시 LLM 기반 엔티티 추출 활성화
ENTITY_EXTRACTION_BATCH_SIZE = 5  # 한 번에 처리할 청크 수 (메모리/속도 최적화)
ENTITY_TYPES = [
    "person",       # 인물명 (예: 홍길동, 김철수)
    "organization", # 조직명 (예: 삼성전자, 현대자동차)
    "date_value",   # 날짜/기간 (예: 2025년 1월, 3개월)
    "money",        # 금액 (예: 1,000만원, $500)
    "location",     # 장소 (예: 서울, 2층 회의실)
    "product",      # 제품/서비스명
    "keyword"       # 핵심 키워드
]


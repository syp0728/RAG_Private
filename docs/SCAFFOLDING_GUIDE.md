# 🏗️ Private RAG 시스템 스캐폴딩 가이드

> 소스코드 없이 처음부터 프로젝트를 직접 구축하는 완전 가이드

---

## 📋 목차

1. [개요](#1-개요)
2. [사전 준비](#2-사전-준비)
3. [프로젝트 구조 생성](#3-프로젝트-구조-생성)
4. [백엔드 구현](#4-백엔드-구현)
5. [프론트엔드 구현](#5-프론트엔드-구현)
6. [AI 모델 설정](#6-ai-모델-설정)
7. [실행 및 테스트](#7-실행-및-테스트)

---

## 1. 개요

### 이 가이드의 목적

소스코드가 전혀 없는 상태에서 Private RAG 시스템을 처음부터 구축하는 방법을 안내합니다.

### 최종 결과물

```
RAG_Private/
├── backend/           # Python Flask API 서버
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── core/
│       ├── rag_system.py
│       ├── document_processor.py
│       ├── file_manager.py
│       └── filename_parser.py
├── frontend/          # React + Vite 웹 UI
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       └── components/
├── data/              # 데이터 저장소
│   ├── uploads/
│   └── chroma_db/
└── models/            # AI 모델 캐시
```

---

## 2. 사전 준비

### 2.1 필수 소프트웨어 설치

| 소프트웨어 | 버전 | 다운로드 |
|-----------|------|----------|
| Python | 3.11.x | https://www.python.org/downloads/release/python-3119/ |
| Node.js | 18+ LTS | https://nodejs.org/ |
| Ollama | 최신 | https://ollama.com/download |

> ⚠️ **중요**: Python 설치 시 "Add Python to PATH" 반드시 체크!

### 2.2 설치 확인

```powershell
python --version   # Python 3.11.x
node --version     # v18.x.x 이상
npm --version      # 9.x.x 이상
ollama --version   # ollama version 0.x.x
```

---

## 3. 프로젝트 구조 생성

### 3.1 루트 폴더 생성

```powershell
# 작업 위치로 이동
cd C:\Users\사용자이름\Documents

# 프로젝트 폴더 생성
mkdir RAG_Private
cd RAG_Private

# 하위 폴더 생성
mkdir backend
mkdir backend\core
mkdir frontend
mkdir frontend\src
mkdir frontend\src\components
mkdir frontend\src\services
mkdir data
mkdir data\uploads
mkdir data\chroma_db
mkdir models
mkdir docs
```

### 3.2 폴더 구조 확인

```
RAG_Private/
├── backend/
│   └── core/
├── frontend/
│   └── src/
│       ├── components/
│       └── services/
├── data/
│   ├── uploads/
│   └── chroma_db/
├── models/
└── docs/
```

---

## 4. 백엔드 구현

### 4.1 가상환경 생성

```powershell
cd backend
python -m venv venv311
.\venv311\Scripts\Activate.ps1
```

### 4.2 requirements.txt 작성

```powershell
# backend/requirements.txt 생성
```

**파일: `backend/requirements.txt`**
```text
flask==3.0.0
flask-cors==4.0.0
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.22
sentence-transformers==2.3.1
ollama==0.1.7
pypdf2==3.0.1
python-docx==1.1.0
python-multipart==0.0.6
werkzeug==3.0.1

# PDF 표 추출
pdfplumber>=0.10.0
pillow>=10.0.0

# 엑셀 파일 처리
openpyxl>=3.1.0
xlrd>=2.0.0

# 이미지 처리 및 OCR
opencv-python-headless>=4.8.0
easyocr>=1.7.0
numpy>=1.24.0

# 검색 엔진
rank_bm25>=0.2.2
```

### 4.3 패키지 설치

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4.4 config.py 작성

**파일: `backend/config.py`**
```python
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
EMBEDDING_DEVICE = "cpu"

# ChromaDB 설정
CHROMA_COLLECTION_NAME = "enterprise_documents"
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR)

# 파일 업로드 설정
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"
}

# RAG 설정
TOP_K_RESULTS = 40
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 컨텍스트 구성 설정
MAX_CHUNKS_PER_FILE = 15
MIN_CONTEXT_COUNT = 15
MAX_CONTEXT_COUNT = 30

# 하이브리드 검색 가중치
VECTOR_WEIGHT = 0.4
BM25_WEIGHT = 0.6

# 재순위화 설정
RERANK_TOP_K = 25
RERANK_ENABLED = True

# 엔티티 추출 설정
ENTITY_EXTRACTION_ENABLED = True
ENTITY_EXTRACTION_BATCH_SIZE = 5
ENTITY_TYPES = [
    "person", "organization", "date_value", 
    "money", "location", "product", "keyword"
]
```

---

### 4.5 core/filename_parser.py 작성

**파일: `backend/core/filename_parser.py`**
```python
"""파일명 파싱 유틸리티"""
import re
from typing import Dict, Optional

def parse_filename(filename: str) -> Dict[str, Optional[str]]:
    """
    파일명을 파싱하여 메타데이터 추출
    형식: YYMMDD_문서유형_문서제목.확장자
    
    예시:
    - "250211_재직증명서_센싱플러스.pdf" 
      -> {"date": "250211", "doc_type": "재직증명서", "doc_title": "센싱플러스"}
    """
    # 확장자 제거
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # 패턴: (날짜 6자리)_(문서유형)_(문서제목)
    pattern = r'^(\d{6})_(.+?)_(.+)$'
    match = re.match(pattern, name_without_ext)
    
    if match:
        return {
            "date": match.group(1),
            "doc_type": match.group(2),
            "doc_title": match.group(3),
            "parsed": True
        }
    else:
        return {
            "date": None,
            "doc_type": None,
            "doc_title": None,
            "parsed": False
        }

def format_date(date_str: str) -> str:
    """날짜 문자열을 읽기 쉬운 형식으로 변환"""
    if not date_str or len(date_str) != 6:
        return date_str
    
    try:
        year = "20" + date_str[:2]
        month = date_str[2:4]
        day = date_str[4:6]
        return f"{year}년 {month}월 {day}일"
    except:
        return date_str
```

---

### 4.6 core/file_manager.py 작성

**파일: `backend/core/file_manager.py`**
```python
import hashlib
import json
from pathlib import Path
from config import UPLOAD_DIR
from .filename_parser import parse_filename

class FileManager:
    """파일 업로드 및 다운로드 관리"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.file_registry = {}
        self.metadata_file = self.upload_dir / ".file_metadata.json"
        self._load_metadata()
    
    def _generate_file_id(self, filename):
        """파일 ID 생성 (해시 기반)"""
        return hashlib.md5(filename.encode()).hexdigest()
    
    def _load_metadata(self):
        """메타데이터 파일에서 원본 파일명 정보 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    for file_id, info in metadata.items():
                        safe_filename = info.get('safe_filename', '')
                        file_path = self.upload_dir / f"{file_id}_{safe_filename}"
                        if file_path.exists():
                            self.file_registry[file_id] = {
                                "id": file_id,
                                "filename": info.get('original_filename', safe_filename),
                                "path": file_path,
                                "size": file_path.stat().st_size
                            }
            except Exception as e:
                print(f"메타데이터 로드 오류: {e}")
    
    def _save_metadata(self):
        """메타데이터 파일에 원본 파일명 정보 저장"""
        metadata = {}
        for file_id, info in self.file_registry.items():
            if info["path"].exists():
                parsed_info = parse_filename(info["filename"])
                file_metadata = {
                    "original_filename": info["filename"],
                    "safe_filename": info["path"].name.split("_", 1)[1] if "_" in info["path"].name else info["path"].name
                }
                if parsed_info["parsed"]:
                    file_metadata.update({
                        "date": parsed_info["date"],
                        "doc_type": parsed_info["doc_type"],
                        "doc_title": parsed_info["doc_title"]
                    })
                metadata[file_id] = file_metadata
        
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메타데이터 저장 오류: {e}")
    
    def save_file(self, file, safe_filename, original_filename=None):
        """파일 저장 및 ID 반환"""
        if original_filename is None:
            original_filename = safe_filename
        
        file_id = self._generate_file_id(original_filename)
        file_path = self.upload_dir / f"{file_id}_{safe_filename}"
        
        file.save(str(file_path))
        
        self.file_registry[file_id] = {
            "id": file_id,
            "filename": original_filename,
            "path": file_path,
            "size": file_path.stat().st_size
        }
        
        self._save_metadata()
        return file_path
    
    def get_file_path(self, file_id):
        """파일 ID로 파일 경로 조회"""
        if file_id in self.file_registry:
            return self.file_registry[file_id]["path"]
        
        for file_path in self.upload_dir.glob(f"{file_id}_*"):
            return file_path
        return None
    
    def list_files(self):
        """업로드된 파일 목록 반환"""
        files = []
        for file_id, file_info in self.file_registry.items():
            if file_info["path"].exists():
                files.append({
                    "id": file_id,
                    "filename": file_info["filename"],
                    "size": file_info["size"]
                })
        return files
    
    def delete_file(self, file_id):
        """파일 삭제"""
        file_path = self.get_file_path(file_id)
        if file_path and file_path.exists():
            file_path.unlink()
            if file_id in self.file_registry:
                del self.file_registry[file_id]
            self._save_metadata()
            return True
        return False
```

---

### 4.7 core/logger.py 작성

**파일: `backend/core/logger.py`**
```python
"""컬러 로깅 유틸리티"""
from datetime import datetime

class Logger:
    """터미널 컬러 로거"""
    
    # ANSI 색상 코드
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    
    def _log(self, level: str, color: str, tag: str, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        color_code = self.COLORS.get(color, self.COLORS['white'])
        reset = self.COLORS['reset']
        print(f"{color_code}[{timestamp}] [{tag}] {message}{reset}")
    
    def info(self, tag: str, message: str):
        self._log('INFO', 'cyan', tag, message)
    
    def success(self, tag: str, message: str):
        self._log('SUCCESS', 'green', tag, message)
    
    def warning(self, tag: str, message: str):
        self._log('WARNING', 'yellow', tag, message)
    
    def error(self, tag: str, message: str):
        self._log('ERROR', 'red', tag, message)

logger = Logger()
```

---

### 4.8 core/__init__.py 작성

**파일: `backend/core/__init__.py`**
```python
# core 패키지 초기화
```

---

### 4.9 core/document_processor.py 작성 (핵심)

> ⚠️ 이 파일은 매우 길기 때문에 핵심 구조만 제시합니다.

**파일: `backend/core/document_processor.py`**
```python
"""문서 처리 모듈 - PDF, DOCX, Excel 파싱"""
import os
from pathlib import Path
from typing import List, Dict, Any

class DocumentProcessor:
    """문서 파싱 및 청킹 처리"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ocr_reader = None  # EasyOCR (지연 로딩)
    
    def process(self, file_path: str, filename: str = None) -> List[Dict[str, Any]]:
        """파일을 처리하여 청크 리스트 반환"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if filename is None:
            filename = path.name
        
        # 파일 형식별 처리
        if ext == '.pdf':
            return self._process_pdf(path, filename)
        elif ext == '.docx':
            return self._process_docx(path, filename)
        elif ext in ['.xlsx', '.xls']:
            return self._process_excel(path, filename)
        elif ext == '.txt':
            return self._process_text(path, filename)
        elif ext in ['.png', '.jpg', '.jpeg']:
            return self._process_image(path, filename)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {ext}")
    
    def _process_pdf(self, path: Path, filename: str) -> List[Dict]:
        """PDF 파일 처리"""
        from .logger import logger
        import pdfplumber
        
        chunks = []
        logger.info("PDF", f"Processing: {filename}")
        
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # 텍스트 추출
                text = page.extract_text() or ""
                
                # 표 추출
                tables = page.extract_tables()
                if tables:
                    logger.info("PDF", f"Page {page_num}: {len(tables)} tables found")
                    for table in tables:
                        table_text = self._table_to_markdown(table)
                        if table_text:
                            chunks.append({
                                "text": table_text,
                                "page": page_num,
                                "type": "table",
                                "metadata": {"has_table": True}
                            })
                
                # 일반 텍스트 청킹
                if text.strip():
                    text_chunks = self._chunk_text(text, page_num)
                    chunks.extend(text_chunks)
        
        logger.success("PDF", f"Total chunks: {len(chunks)}")
        return chunks
    
    def _process_docx(self, path: Path, filename: str) -> List[Dict]:
        """DOCX 파일 처리"""
        from docx import Document
        
        doc = Document(str(path))
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return self._chunk_text(full_text, page=1)
    
    def _process_excel(self, path: Path, filename: str) -> List[Dict]:
        """Excel 파일 처리"""
        import openpyxl
        
        chunks = []
        wb = openpyxl.load_workbook(str(path), data_only=True)
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            table_data = []
            
            for row in sheet.iter_rows(values_only=True):
                if any(cell is not None for cell in row):
                    table_data.append([str(cell) if cell else "" for cell in row])
            
            if table_data:
                markdown = self._table_to_markdown(table_data)
                chunks.append({
                    "text": f"[시트: {sheet_name}]\n{markdown}",
                    "page": 1,
                    "type": "table",
                    "metadata": {"has_table": True, "sheet": sheet_name}
                })
        
        return chunks
    
    def _process_text(self, path: Path, filename: str) -> List[Dict]:
        """텍스트 파일 처리"""
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        return self._chunk_text(text, page=1)
    
    def _process_image(self, path: Path, filename: str) -> List[Dict]:
        """이미지 파일 OCR 처리"""
        if self.ocr_reader is None:
            import easyocr
            self.ocr_reader = easyocr.Reader(['ko', 'en'])
        
        results = self.ocr_reader.readtext(str(path))
        text = "\n".join([r[1] for r in results])
        return self._chunk_text(text, page=1)
    
    def _chunk_text(self, text: str, page: int) -> List[Dict]:
        """텍스트를 청크로 분할"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "page": page,
                    "type": "text",
                    "metadata": {}
                })
                # 오버랩
                overlap_words = current_chunk[-20:]  # 마지막 20단어
                current_chunk = overlap_words
                current_length = sum(len(w) for w in current_chunk)
            
            current_chunk.append(word)
            current_length += len(word) + 1
        
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "page": page,
                "type": "text",
                "metadata": {}
            })
        
        return chunks
    
    def _table_to_markdown(self, table: List[List]) -> str:
        """표 데이터를 Markdown 형식으로 변환"""
        if not table or not table[0]:
            return ""
        
        lines = []
        
        # 헤더
        header = [str(cell) if cell else "" for cell in table[0]]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # 데이터 행
        for row in table[1:]:
            cells = [str(cell) if cell else "" for cell in row]
            # 열 개수 맞추기
            while len(cells) < len(header):
                cells.append("")
            lines.append("| " + " | ".join(cells[:len(header)]) + " |")
        
        return "\n".join(lines)
```

---

### 4.10 core/rag_system.py 작성 (핵심)

> ⚠️ 이 파일도 매우 길기 때문에 핵심 구조만 제시합니다.

**파일: `backend/core/rag_system.py`**
```python
"""RAG 시스템 핵심 모듈"""
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
from rank_bm25 import BM25Okapi

from config import (
    CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL, EMBEDDING_DEVICE,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    TOP_K_RESULTS, RERANK_TOP_K, RERANK_ENABLED,
    VECTOR_WEIGHT, BM25_WEIGHT,
    MIN_CONTEXT_COUNT, MAX_CONTEXT_COUNT
)
from .document_processor import DocumentProcessor
from .filename_parser import parse_filename
from .logger import logger


class RAGSystem:
    """RAG 시스템 메인 클래스"""
    
    def __init__(self):
        logger.info("RAG", "=== RAG System 초기화 ===")
        
        # ChromaDB 초기화
        logger.info("RAG", "ChromaDB 연결...")
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # 임베딩 모델 로딩
        logger.info("RAG", f"임베딩 모델 로딩: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE
        )
        
        # Ollama 설정
        self.ollama_base_url = OLLAMA_BASE_URL
        self.ollama_model = OLLAMA_MODEL
        logger.info("RAG", f"Ollama 모델: {OLLAMA_MODEL}")
        
        # 문서 처리기
        self.document_processor = DocumentProcessor()
        
        # 시스템 프롬프트
        self.system_prompt = """너는 기업 내부 문서를 분석하는 AI 어시스턴트이다.
제공된 컨텍스트만을 기반으로 답변하고, 정보가 없으면 "해당 정보가 없습니다"라고 답해라.
답변 끝에 반드시 [출처: 파일명, 페이지 X]를 표시하라."""
        
        logger.success("RAG", "=== 초기화 완료 ===")
    
    def index_document(self, file_path: str, filename: str = None) -> Dict:
        """문서를 인덱싱"""
        path = Path(file_path)
        if filename is None:
            filename = path.name
        
        logger.info("INDEX", f"문서 인덱싱 시작: {filename}")
        
        # 파일 ID 생성
        file_id = hashlib.md5(filename.encode()).hexdigest()
        
        # 파일명에서 메타데이터 추출
        parsed = parse_filename(filename)
        file_ext = path.suffix.lower()
        
        # 문서 처리
        chunks = self.document_processor.process(str(path), filename)
        logger.info("INDEX", f"청크 수: {len(chunks)}")
        
        # 청크 저장
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_id}_{i}"
            
            # 임베딩 생성
            embedding = self.embedding_model.encode(chunk["text"]).tolist()
            
            # 메타데이터 구성
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "page": chunk.get("page", 1),
                "type": chunk.get("type", "text"),
                "chunk_index": i,
                "file_extension": file_ext,
                "has_table": chunk.get("metadata", {}).get("has_table", False),
            }
            
            if parsed["parsed"]:
                metadata.update({
                    "date": parsed["date"],
                    "doc_type": parsed["doc_type"],
                    "doc_title": parsed["doc_title"],
                })
            
            # ChromaDB에 저장
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[metadata]
            )
        
        logger.success("INDEX", f"인덱싱 완료: {len(chunks)} 청크")
        
        return {
            "file_id": file_id,
            "chunks_count": len(chunks)
        }
    
    def query(self, query_text: str) -> Dict:
        """질문에 대한 답변 생성"""
        logger.info("QUERY", f"질문: {query_text[:50]}...")
        
        # 1. 쿼리 임베딩
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        # 2. 벡터 검색
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K_RESULTS,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"][0]:
            return {
                "answer": "관련 문서를 찾을 수 없습니다.",
                "sources": [],
                "has_answer": False
            }
        
        # 3. 컨텍스트 구성
        context_parts = []
        sources = []
        
        for i, (doc, meta) in enumerate(zip(
            results["documents"][0][:RERANK_TOP_K],
            results["metadatas"][0][:RERANK_TOP_K]
        )):
            filename = meta.get("filename", "알 수 없음")
            page = meta.get("page", "?")
            context_parts.append(f"[문서 {i+1}: {filename}, 페이지 {page}]\n{doc}")
            sources.append({
                "filename": filename,
                "page": page,
                "doc_type": meta.get("doc_type"),
            })
        
        context = "\n\n".join(context_parts)
        
        # 4. LLM으로 답변 생성
        user_prompt = f"""컨텍스트:
{context}

질문: {query_text}

위 컨텍스트를 기반으로 질문에 답변해주세요."""
        
        client = ollama.Client(host=self.ollama_base_url)
        response = client.chat(
            model=self.ollama_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": 0.0,
                "top_p": 0.7,
                "num_predict": 1500,
            }
        )
        
        answer = response["message"]["content"]
        logger.success("QUERY", "답변 생성 완료")
        
        return {
            "answer": answer,
            "sources": sources[:5],  # 상위 5개 출처만
            "has_answer": True
        }
    
    def delete_document(self, file_id: str) -> int:
        """문서 삭제"""
        results = self.collection.get(
            where={"file_id": file_id},
            include=["metadatas"]
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.success("DELETE", f"{len(results['ids'])} 청크 삭제")
            return len(results["ids"])
        
        return 0
    
    def delete_document_by_filename(self, filename: str) -> int:
        """파일명으로 문서 삭제"""
        results = self.collection.get(
            where={"filename": filename},
            include=["metadatas"]
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            return len(results["ids"])
        
        return 0
    
    def check_duplicate_document(self, filename: str) -> Dict:
        """중복 문서 확인"""
        file_id = hashlib.md5(filename.encode()).hexdigest()
        results = self.collection.get(
            where={"file_id": file_id},
            include=["metadatas"]
        )
        
        if results["ids"]:
            return {
                "is_duplicate": True,
                "message": f"'{filename}' 파일이 이미 존재합니다.",
                "existing_file_id": file_id
            }
        
        return {"is_duplicate": False}
    
    def get_all_document_types(self) -> Dict[str, int]:
        """모든 문서 유형과 개수 반환"""
        results = self.collection.get(include=["metadatas"])
        
        doc_types = {}
        seen_files = set()
        
        for meta in results["metadatas"]:
            filename = meta.get("filename")
            if filename and filename not in seen_files:
                seen_files.add(filename)
                doc_type = meta.get("doc_type")
                if doc_type:
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return doc_types
```

---

### 4.11 app.py 작성

**파일: `backend/app.py`**
```python
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from werkzeug.utils import secure_filename
from config import *

# 출력 버퍼링 비활성화
os.environ['PYTHONUNBUFFERED'] = '1'

def check_ollama_running():
    """Ollama 서버가 실행 중인지 확인"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama_server():
    """Ollama 서버를 백그라운드로 시작"""
    print("[OLLAMA] Checking Ollama server status...")
    
    if check_ollama_running():
        print("[OLLAMA] Ollama server is already running")
        return True
    
    print("[OLLAMA] Starting Ollama server...")
    
    try:
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Ollama가 준비될 때까지 대기 (최대 30초)
        for i in range(30):
            time.sleep(1)
            if check_ollama_running():
                print(f"[OLLAMA] Server started (took {i+1}s)")
                return True
        
        print("[OLLAMA] WARNING: Server did not start within 30s")
        return False
        
    except FileNotFoundError:
        print("[OLLAMA] ERROR: 'ollama' command not found")
        return False

# Ollama 서버 자동 시작
start_ollama_server()

from core.rag_system import RAGSystem
from core.file_manager import FileManager

app = Flask(__name__)
CORS(app)

# 시스템 초기화
rag_system = RAGSystem()
file_manager = FileManager()

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        
        # 파일 확장자 검증
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Unsupported: {file_ext}"}), 400
        
        original_filename = file.filename
        
        # 중복 확인
        dup_check = rag_system.check_duplicate_document(original_filename)
        if dup_check["is_duplicate"]:
            return jsonify({"error": "Duplicate", "is_duplicate": True}), 409
        
        # 파일 저장
        safe_filename = secure_filename(file.filename)
        file_path = file_manager.save_file(file, safe_filename, original_filename)
        
        # 인덱싱
        result = rag_system.index_document(file_path, original_filename)
        
        return jsonify({
            "success": True,
            "filename": original_filename,
            "file_id": result["file_id"],
            "chunks_count": result["chunks_count"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files", methods=["GET"])
def list_files():
    try:
        files = file_manager.list_files()
        
        from core.filename_parser import parse_filename
        for f in files:
            parsed = parse_filename(f["filename"])
            f.update({
                "date": parsed.get("date"),
                "doc_type": parsed.get("doc_type"),
                "doc_title": parsed.get("doc_title")
            })
        
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    try:
        # 파일 정보 가져오기
        file_info = None
        for f in file_manager.list_files():
            if f["id"] == file_id:
                file_info = f
                break
        
        # 벡터 DB에서 삭제
        deleted = 0
        if file_info:
            deleted = rag_system.delete_document_by_filename(file_info["filename"])
        if deleted == 0:
            deleted = rag_system.delete_document(file_id)
        
        # 파일 삭제
        file_manager.delete_file(file_id)
        
        return jsonify({"success": True, "deleted_chunks": deleted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/query", methods=["POST"])
def query():
    try:
        data = request.json
        query_text = data.get("query")
        
        if not query_text:
            return jsonify({"error": "Query required"}), 400
        
        result = rag_system.query(query_text)
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
            "has_answer": result["has_answer"]
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "answer": f"오류: {str(e)}",
            "sources": [],
            "has_answer": False
        }), 500

if __name__ == "__main__":
    print("Starting Private RAG API...")
    print(f"Ollama: {OLLAMA_BASE_URL}")
    app.run(host="0.0.0.0", port=5000, debug=False)
```

---

## 5. 프론트엔드 구현

### 5.1 package.json 작성

```powershell
cd ..\frontend
```

**파일: `frontend/package.json`**
```json
{
  "name": "private-rag-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

### 5.2 vite.config.js 작성

**파일: `frontend/vite.config.js`**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

### 5.3 index.html 작성

**파일: `frontend/index.html`**
```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Private RAG System</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### 5.4 src/main.jsx 작성

**파일: `frontend/src/main.jsx`**
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 5.5 src/App.jsx 작성

**파일: `frontend/src/App.jsx`**
```jsx
import { useState, useEffect } from 'react'
import FileManager from './components/FileManager'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // 백엔드 연결 확인
    fetch('/api/health')
      .then(res => res.json())
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false))
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>🔒 Private RAG System</h1>
        <div className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '백엔드 연결됨' : '연결 중...'}
        </div>
      </header>
      
      <nav className="tabs">
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => setActiveTab('chat')}
        >
          💬 채팅
        </button>
        <button 
          className={activeTab === 'files' ? 'active' : ''} 
          onClick={() => setActiveTab('files')}
        >
          📁 파일 관리
        </button>
      </nav>
      
      <main className="main-content">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'files' && <FileManager />}
      </main>
    </div>
  )
}

export default App
```

### 5.6 src/components/ChatInterface.jsx 작성

**파일: `frontend/src/components/ChatInterface.jsx`**
```jsx
import { useState } from 'react'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      })
      
      const data = await response.json()
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer,
        sources: data.sources 
      }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '오류가 발생했습니다: ' + error.message 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            문서에 대해 질문해보세요!
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="content">{msg.content}</div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                출처: {msg.sources.map(s => s.filename).join(', ')}
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="content">생각하는 중...</div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="질문을 입력하세요..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>전송</button>
      </form>
    </div>
  )
}

export default ChatInterface
```

### 5.7 src/components/FileManager.jsx 작성

**파일: `frontend/src/components/FileManager.jsx`**
```jsx
import { useState, useEffect } from 'react'
import './FileManager.css'

function FileManager() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchFiles = async () => {
    try {
      const response = await fetch('/api/files')
      const data = await response.json()
      setFiles(data.files || [])
    } catch (error) {
      console.error('파일 목록 조회 실패:', error)
    }
  }

  useEffect(() => {
    fetchFiles()
  }, [])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setMessage('업로드 중...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setMessage(`✅ 업로드 완료: ${data.chunks_count}개 청크 생성`)
        fetchFiles()
      } else {
        setMessage(`❌ 오류: ${data.error}`)
      }
    } catch (error) {
      setMessage(`❌ 업로드 실패: ${error.message}`)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (fileId, filename) => {
    if (!confirm(`"${filename}"을(를) 삭제하시겠습니까?`)) return

    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setMessage(`✅ "${filename}" 삭제 완료`)
        fetchFiles()
      } else {
        const data = await response.json()
        setMessage(`❌ 삭제 실패: ${data.error}`)
      }
    } catch (error) {
      setMessage(`❌ 삭제 실패: ${error.message}`)
    }
  }

  return (
    <div className="file-manager">
      <div className="upload-section">
        <label className="upload-button">
          📤 파일 업로드
          <input 
            type="file" 
            onChange={handleUpload}
            disabled={uploading}
            accept=".pdf,.docx,.xlsx,.xls,.txt"
          />
        </label>
        {message && <div className="message">{message}</div>}
      </div>
      
      <div className="file-list">
        <h3>업로드된 파일 ({files.length}개)</h3>
        
        {files.length === 0 ? (
          <p className="empty">업로드된 파일이 없습니다.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>파일명</th>
                <th>문서 유형</th>
                <th>날짜</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {files.map(file => (
                <tr key={file.id}>
                  <td>{file.filename}</td>
                  <td>{file.doc_type || '-'}</td>
                  <td>{file.date || '-'}</td>
                  <td>
                    <button 
                      onClick={() => handleDelete(file.id, file.filename)}
                      className="delete-btn"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default FileManager
```

### 5.8 CSS 파일 작성

**파일: `frontend/src/index.css`**
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #333;
}
```

**파일: `frontend/src/App.css`**
```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 1.5rem;
}

.status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.status.connected {
  background: #2ecc71;
}

.status.disconnected {
  background: #e74c3c;
}

.tabs {
  background: #16213e;
  padding: 0 2rem;
  display: flex;
  gap: 0.5rem;
}

.tabs button {
  background: transparent;
  border: none;
  color: #aaa;
  padding: 1rem 1.5rem;
  cursor: pointer;
  font-size: 1rem;
  border-bottom: 3px solid transparent;
}

.tabs button.active {
  color: white;
  border-bottom-color: #3498db;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
```

**파일: `frontend/src/components/ChatInterface.css`**
```css
.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
}

.message {
  margin-bottom: 1rem;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message.user .content {
  background: #3498db;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 0.75rem 1rem;
}

.message.assistant .content {
  background: #f0f0f0;
  border-radius: 18px 18px 18px 4px;
  padding: 0.75rem 1rem;
}

.message .sources {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.5rem;
}

.input-form {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #eee;
  gap: 0.5rem;
}

.input-form input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 1rem;
}

.input-form button {
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
}
```

**파일: `frontend/src/components/FileManager.css`**
```css
.file-manager {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}

.upload-button input {
  display: none;
}

.upload-section .message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.file-list h3 {
  margin-bottom: 1rem;
}

.file-list table {
  width: 100%;
  border-collapse: collapse;
}

.file-list th, .file-list td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.file-list th {
  background: #f8f9fa;
  font-weight: 600;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
}

.empty {
  color: #999;
  text-align: center;
  padding: 2rem;
}
```

### 5.9 패키지 설치

```powershell
npm install
```

---

## 6. AI 모델 설정

### 6.1 LLM 모델 다운로드

```powershell
# llama3.1 8B 모델 다운로드 (약 4.7GB)
ollama pull llama3.1:8b-instruct-q4_K_M

# 확인
ollama list
```

### 6.2 임베딩 모델 사전 다운로드 (선택)

```powershell
cd backend
.\venv311\Scripts\Activate.ps1

python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

---

## 7. 실행 및 테스트

### 7.1 백엔드 실행

**터미널 1**:
```powershell
cd C:\Users\사용자이름\Documents\RAG_Private\backend
.\venv311\Scripts\Activate.ps1
python -u app.py
```

**정상 출력**:
```
[OLLAMA] Checking Ollama server status...
[OLLAMA] Ollama server is already running
=== RAG System 초기화 ===
ChromaDB 연결...
임베딩 모델 로딩: BAAI/bge-m3
=== 초기화 완료 ===
Starting Private RAG API...
 * Running on http://0.0.0.0:5000
```

### 7.2 프론트엔드 실행

**터미널 2**:
```powershell
cd C:\Users\사용자이름\Documents\RAG_Private\frontend
npm run dev
```

**정상 출력**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 7.3 테스트

1. 브라우저에서 http://localhost:5173 접속
2. "파일 관리" 탭에서 PDF 파일 업로드
3. "채팅" 탭에서 질문 입력
4. AI 답변 확인!

---

## 🎉 완료!

처음부터 Private RAG 시스템을 성공적으로 구축했습니다!

### 다음 단계

- 고급 기능 추가: 하이브리드 검색, Re-Ranking
- 표 처리 고도화: OpenCV 표 선 감지
- UI 개선: 문서 유형 필터, 검색 기록

### 참고 문서

- [기술 명세서](./TECHNICAL_SPEC.md)
- [파이프라인 상세](./PIPELINE.md)

---

*Last Updated: 2026-01-29*


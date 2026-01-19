import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama
from config import *
from .document_processor import DocumentProcessor
from .filename_parser import parse_filename

class RAGSystem:
    """RAG 시스템 클래스 - 하이브리드 자원 분배"""
    
    def __init__(self):
        # ChromaDB 클라이언트 초기화
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 컬렉션 가져오기 또는 생성
        try:
            self.collection = self.chroma_client.get_collection(CHROMA_COLLECTION_NAME)
        except:
            self.collection = self.chroma_client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        
        # 임베딩 모델 초기화 (CPU에서 실행)
        print(f"Loading embedding model on {EMBEDDING_DEVICE}...")
        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE
        )
        
        # 문서 프로세서 초기화
        self.doc_processor = DocumentProcessor()
        
        # Ollama 연결 확인 (GPU에서 실행됨)
        self.ollama_base_url = OLLAMA_BASE_URL
        self.ollama_model = OLLAMA_MODEL
        
        # Ollama 연결 테스트
        try:
            host = OLLAMA_BASE_URL.replace("http://", "").replace("https://", "")
            test_client = ollama.Client(host=host)
            # 간단한 연결 테스트
            models = test_client.list()
            print(f"✅ Ollama 연결 확인: {OLLAMA_BASE_URL}")
            print(f"   사용 가능한 모델: {[m['name'] for m in models.get('models', [])]}")
            
            # 모델 존재 확인
            model_names = [m['name'] for m in models.get('models', [])]
            if self.ollama_model not in model_names:
                print(f"⚠️ 경고: 모델 '{self.ollama_model}'이 설치되지 않았습니다.")
                print(f"   다음 명령어로 다운로드하세요: ollama pull {self.ollama_model}")
        except Exception as e:
            print(f"⚠️ Ollama 연결 확인 실패: {e}")
            print(f"   Ollama가 실행 중인지 확인하세요: ollama serve")
        
        # 시스템 프롬프트 (할루시네이션 방지 강화)
        self.system_prompt = """너는 기업 내부 보안 문서를 분석하는 전문 AI 어시스턴트이다. 
반드시 제공된 컨텍스트(Context)와 메타데이터만을 근거로 답변하며, 외부 지식 사용을 엄격히 금지한다.

### 1. 검색 및 필터링 규칙 (Metadata Priority)
- 질의에 파일명, 날짜(예: 250211), 문서 유형이 포함된 경우, 메타데이터가 정확히 일치하는 청크만 추출하여 답변한다.
- 여러 문서가 검색되었더라도 질의와 무관한 파일의 내용은 무시한다.

### 2. 답변 생성 원칙 (No-Hallucination)
- 컨텍스트에 없는 정보는 추측하지 않고 "지식 베이스에 없는 내용입니다"라고만 답한다.
- 추정, 의견, 상식 추가를 금지하며 오직 텍스트에 명시된 사실만 전달한다.
- 동일한 정보가 여러 청크에 걸쳐 있다면 중복을 제거하고 하나로 병합하여 요약한다.

### 3. 출력 형식 제한 (Plain Text Only)
- **마크다운 금지**: 어떠한 경우에도 마크다운 문법(`**`, `#`, `-` 등)을 사용하지 않는다.
- **순수 텍스트**: 모든 강조와 구조화는 줄바꿈과 띄어쓰기 등 순수 텍스트로만 표현한다.
- **표 처리**: 표 데이터는 마크다운 대신 '항목: 내용' 형태의 텍스트 리스트로 변환하여 출력한다.

### 4. 소스 표기 규격
- 답변 하단에 [출처: 파일명, 페이지 X] 형식을 반드시 포함한다.
- 여러 페이지를 참고한 경우 [출처: 파일명, 페이지 X, Y, Z]와 같이 병합 표기한다.

### 답변 가이드라인:
- 답변 (Plain Text)
- [출처: 파일명, 페이지 번호]"""
    
    def _get_file_id(self, file_path: Path) -> str:
        """파일 ID 생성"""
        return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def check_duplicate_document(self, filename: str) -> Dict:
        """문서 중복 확인
        
        Returns:
            {
                "is_duplicate": bool,
                "existing_file_id": str or None,
                "message": str
            }
        """
        try:
            # 벡터 DB에서 같은 파일명을 가진 문서 검색
            existing_docs = self.collection.get(where={"filename": filename})
            
            if existing_docs.get("ids") and len(existing_docs["ids"]) > 0:
                # 중복 문서 발견
                # 첫 번째 문서의 메타데이터에서 file_id 추출
                first_metadata = existing_docs["metadatas"][0]
                existing_file_id = first_metadata.get("file_id")
                date = first_metadata.get("date")
                doc_type = first_metadata.get("doc_type")
                doc_title = first_metadata.get("doc_title")
                
                # 메시지 구성
                message_parts = [f"파일명 '{filename}'과(와) 동일한 문서가 이미 존재합니다."]
                if date:
                    message_parts.append(f"날짜: {date}")
                if doc_type:
                    message_parts.append(f"문서 유형: {doc_type}")
                if doc_title:
                    message_parts.append(f"문서 제목: {doc_title}")
                
                message = " ".join(message_parts)
                
                return {
                    "is_duplicate": True,
                    "existing_file_id": existing_file_id,
                    "message": message
                }
            else:
                return {
                    "is_duplicate": False,
                    "existing_file_id": None,
                    "message": "중복 문서가 없습니다."
                }
        except Exception as e:
            print(f"[RAG] 중복 문서 확인 오류: {e}")
            # 오류 발생 시 중복이 아닌 것으로 간주 (안전한 선택)
            return {
                "is_duplicate": False,
                "existing_file_id": None,
                "message": f"중복 확인 중 오류 발생: {str(e)}"
            }
    
    def index_document(self, file_path: Path, filename: str) -> Dict:
        """문서를 인덱싱하여 벡터 DB에 저장"""
        file_id = self._get_file_id(file_path)
        
        # 문서 처리 (Layout-aware)
        chunks = self.doc_processor.extract_text_with_layout(file_path)
        
        # 기존 문서 청크 삭제 (같은 파일 재업로드 시)
        try:
            existing = self.collection.get(where={"file_id": file_id})
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
        except:
            pass
        
        # 임베딩 생성 (CPU)
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        ).tolist()
        
        # 파일명 파싱하여 메타데이터 추출
        parsed_info = parse_filename(filename)
        
        # 메타데이터 준비
        ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_id}_chunk_{i}"
            ids.append(chunk_id)
            
            # 기본 메타데이터
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "page": chunk["page"],
                "type": chunk["type"],
                "chunk_index": i
            }
            
            # 파싱된 정보 추가
            if parsed_info["parsed"]:
                metadata["date"] = parsed_info["date"]
                metadata["doc_type"] = parsed_info["doc_type"]
                metadata["doc_title"] = parsed_info["doc_title"]
            else:
                metadata["date"] = None
                metadata["doc_type"] = None
                metadata["doc_title"] = None
            
            metadatas.append(metadata)
        
        # ChromaDB에 저장
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return {
            "file_id": file_id,
            "chunks_count": len(chunks)
        }
    
    def get_document_count_by_type(self, doc_type: str) -> int:
        """문서 유형별 고유 문서 개수 조회"""
        try:
            # 해당 문서 유형의 모든 문서 가져오기
            results = self.collection.get(where={"doc_type": doc_type})
            
            if not results["ids"]:
                return 0
            
            # 고유한 filename 개수 세기
            unique_filenames = set()
            for metadata in results["metadatas"]:
                filename = metadata.get("filename")
                if filename:
                    unique_filenames.add(filename)
            
            return len(unique_filenames)
        except Exception as e:
            print(f"[RAG] 문서 유형별 개수 조회 오류: {e}")
            return 0
    
    def get_all_document_types(self) -> Dict[str, int]:
        """모든 문서 유형별 문서 개수 조회"""
        try:
            # 모든 문서 가져오기
            all_docs = self.collection.get()
            
            # 문서 유형별로 그룹화
            doc_type_counts = {}
            for metadata in all_docs["metadatas"]:
                doc_type = metadata.get("doc_type")
                filename = metadata.get("filename")
                
                if doc_type and filename:
                    if doc_type not in doc_type_counts:
                        doc_type_counts[doc_type] = set()
                    doc_type_counts[doc_type].add(filename)
            
            # 세트를 개수로 변환
            return {doc_type: len(filenames) for doc_type, filenames in doc_type_counts.items()}
        except Exception as e:
            print(f"[RAG] 문서 유형 목록 조회 오류: {e}")
            return {}
    
    def query(self, query_text: str) -> Dict:
        """RAG 질의 처리"""
        import time
        import re
        total_start = time.time()
        
        # 문서 유형 관련 질문 감지
        doc_type_info = None
        doc_type_mentioned = None
        doc_titles_info = None
        
        # 질문에서 문서 유형 추출 시도
        all_doc_types = self.get_all_document_types()
        for doc_type in all_doc_types.keys():
            if doc_type in query_text:
                doc_type_mentioned = doc_type
                doc_type_info = f"{doc_type} 문서는 총 {all_doc_types[doc_type]}개입니다."
                print(f"[RAG] 문서 유형 감지: {doc_type}, 개수: {all_doc_types[doc_type]}")
                break
        
        # "몇 개", "개수", "총" 등의 키워드로 문서 개수 질문 감지
        count_keywords = ["몇 개", "개수", "총", "몇개", "개 있", "개 있나"]
        is_count_query = any(keyword in query_text for keyword in count_keywords)
        
        # 문서 제목/목록 관련 질문 감지
        title_keywords = ["문서제목", "문서 제목", "제목", "문서명", "파일명"]
        list_keywords = ["문서를 모두", "문서 목록", "문서 나열", "문서를 알려", "문서를 말해", "문서를 보여"]
        is_title_query = any(keyword in query_text for keyword in title_keywords)
        is_list_query = any(keyword in query_text for keyword in list_keywords)
        
        # 키워드 추출 (예: "tlc와 관련된 문서")
        keyword = None
        keyword_patterns = [
            r"(\w+)\s*와\s*관련된",
            r"(\w+)\s*관련",
            r"(\w+)\s*문서"
        ]
        for pattern in keyword_patterns:
            match = re.search(pattern, query_text, re.IGNORECASE)
            if match:
                keyword = match.group(1).lower()
                print(f"[RAG] 키워드 감지: {keyword}")
                break
        
        # 특정 문서 전체 검색 감지 (예: "250211 재직증명서에서 문서 전체를 확인")
        specific_doc_date = None
        specific_doc_type = None
        specific_doc_filename = None
        
        # 날짜 패턴 추출 (6자리 숫자: 250211)
        date_pattern = r'(\d{6})'
        date_match = re.search(date_pattern, query_text)
        if date_match:
            specific_doc_date = date_match.group(1)
            print(f"[RAG] 날짜 감지: {specific_doc_date}")
        
        # 파일명 감지 및 필터링 (Self-Query Retriever 기능)
        specific_filename = None
        detected_filenames = []  # 감지된 모든 파일명 (후처리 필터링용)
        try:
            # 벡터 DB에 저장된 모든 파일명 가져오기
            all_docs_for_filename_check = self.collection.get()
            all_filenames = set()
            for metadata in all_docs_for_filename_check.get("metadatas", []):
                filename = metadata.get("filename")
                if filename:
                    all_filenames.add(filename)
            
            # 1단계: 날짜와 문서 유형이 모두 있으면 정확한 파일명 찾기
            if specific_doc_date and doc_type_mentioned:
                matching_docs = self.collection.get(where={
                    "$and": [
                        {"date": specific_doc_date},
                        {"doc_type": doc_type_mentioned}
                    ]
                })
                if matching_docs.get("metadatas"):
                    # 고유한 파일명 추출
                    unique_filenames = set()
                    for metadata in matching_docs["metadatas"]:
                        filename = metadata.get("filename")
                        if filename:
                            unique_filenames.add(filename)
                    
                    if len(unique_filenames) == 1:
                        specific_filename = list(unique_filenames)[0]
                        detected_filenames.append(specific_filename)
                        print(f"[RAG] 파일명 감지 (날짜+유형 매칭): {specific_filename}")
                    elif len(unique_filenames) > 1:
                        # 여러 파일이 있으면 질문에서 파일명 부분 매칭 시도
                        for filename in unique_filenames:
                            filename_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
                            filename_parts = filename_without_ext.split('_')
                            for part in filename_parts:
                                if len(part) > 3 and part in query_text:
                                    specific_filename = filename
                                    detected_filenames.append(filename)
                                    print(f"[RAG] 파일명 감지 (부분 매칭): {specific_filename}")
                                    break
                            if specific_filename:
                                break
                        
                        # 부분 매칭이 실패하면 첫 번째 파일 선택
                        if not specific_filename:
                            specific_filename = list(unique_filenames)[0]
                            detected_filenames.append(specific_filename)
                            print(f"[RAG] 파일명 감지 (날짜+유형 매칭, 첫 번째 파일 선택): {specific_filename}")
            
            # 2단계: 질문에서 직접 파일명 찾기 (전체 파일명 또는 확장자 제거한 파일명)
            if not specific_filename:
                for filename in all_filenames:
                    filename_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    
                    # 전체 파일명 매칭 (정확한 매칭 우선)
                    if filename in query_text:
                        specific_filename = filename
                        detected_filenames.append(filename)
                        print(f"[RAG] 파일명 감지 (전체 파일명 매칭): {specific_filename}")
                        break
                    
                    # 확장자 제거한 파일명 매칭
                    if filename_without_ext in query_text:
                        specific_filename = filename
                        detected_filenames.append(filename)
                        print(f"[RAG] 파일명 감지 (확장자 제거 매칭): {specific_filename}")
                        break
                    
                    # 파일명의 주요 부분 매칭 (예: "재직증명서", "센싱플러스")
                    # 단, 다른 파일명과 겹치지 않는 고유한 부분만 매칭
                    filename_parts = filename_without_ext.split('_')
                    for part in filename_parts:
                        if len(part) > 3 and part in query_text:
                            # 다른 파일명에도 같은 부분이 있는지 확인
                            is_unique = True
                            for other_filename in all_filenames:
                                if other_filename != filename and part in other_filename:
                                    is_unique = False
                                    break
                            
                            if is_unique:
                                specific_filename = filename
                                detected_filenames.append(filename)
                                print(f"[RAG] 파일명 감지 (고유 부분 매칭): {specific_filename}")
                                break
                    
                    if specific_filename:
                        break
            
            # 3단계: 파일명의 일부가 질문에 포함되어 있는지 확인 (더 넓은 검색)
            if not specific_filename:
                for filename in all_filenames:
                    filename_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    filename_parts = filename_without_ext.split('_')
                    
                    # 파일명의 여러 부분이 질문에 포함되어 있는지 확인
                    matched_parts = [part for part in filename_parts if len(part) > 2 and part in query_text]
                    if len(matched_parts) >= 2:  # 최소 2개 이상의 부분이 매칭되면
                        specific_filename = filename
                        detected_filenames.append(filename)
                        print(f"[RAG] 파일명 감지 (다중 부분 매칭): {specific_filename}")
                        break
            
            # 감지된 파일명이 여러 개인 경우 로그 출력
            if len(detected_filenames) > 1:
                print(f"[RAG] 경고: 여러 파일명이 감지됨: {detected_filenames}, 첫 번째 파일 사용: {specific_filename}")
                
        except Exception as e:
            print(f"[RAG] 파일명 감지 오류: {e}")
            import traceback
            traceback.print_exc()
        
        # "전체", "모든", "나열" 키워드 감지
        full_document_keywords = ["전체", "모든", "나열", "전부", "다", "모두"]
        is_full_document_query = any(keyword in query_text for keyword in full_document_keywords)
        
        # 특정 문서 전체 검색인 경우 해당 문서의 모든 청크를 페이지 순서대로 가져오기
        if specific_doc_date and (doc_type_mentioned or is_full_document_query):
            try:
                print(f"[RAG] 특정 문서 전체 검색 모드: 날짜={specific_doc_date}, 문서유형={doc_type_mentioned}")
                
                # 필터 조건 설정 (ChromaDB 형식: $and 연산자 사용)
                where_filter = None
                if specific_doc_date and doc_type_mentioned:
                    where_filter = {
                        "$and": [
                            {"date": specific_doc_date},
                            {"doc_type": doc_type_mentioned}
                        ]
                    }
                elif specific_doc_date:
                    where_filter = {"date": specific_doc_date}
                elif doc_type_mentioned:
                    where_filter = {"doc_type": doc_type_mentioned}
                
                # 해당 조건의 모든 문서 가져오기
                if where_filter:
                    all_results = self.collection.get(where=where_filter)
                else:
                    all_results = self.collection.get()
                
                if all_results["metadatas"]:
                    # 파일명별로 그룹화하고 페이지 순서대로 정렬
                    doc_chunks = {}
                    for i, metadata in enumerate(all_results["metadatas"]):
                        filename = metadata.get("filename")
                        page = metadata.get("page", 0)
                        doc_text = all_results["documents"][i]
                        
                        if filename:
                            if filename not in doc_chunks:
                                doc_chunks[filename] = []
                            doc_chunks[filename].append({
                                "page": page,
                                "text": doc_text,
                                "metadata": metadata
                            })
                    
                    # 각 파일의 청크를 페이지 순서대로 정렬
                    for filename in doc_chunks:
                        doc_chunks[filename].sort(key=lambda x: x["page"])
                    
                    # 파일 선택 로직
                    if doc_chunks:
                        # 날짜와 문서 유형이 모두 지정된 경우, 모든 매칭 파일의 청크를 병합
                        if specific_doc_date and doc_type_mentioned:
                            # 모든 파일의 청크를 병합 (날짜와 문서 유형이 정확히 일치하는 모든 파일)
                            all_chunks = []
                            for filename, file_chunks in doc_chunks.items():
                                all_chunks.extend(file_chunks)
                                print(f"[RAG] 파일 포함: {filename}, {len(file_chunks)}개 청크")
                            
                            # 페이지 순서대로 정렬
                            all_chunks.sort(key=lambda x: (x["metadata"].get("filename", ""), x["page"]))
                            chunks = all_chunks
                            
                            if len(doc_chunks) > 1:
                                print(f"[RAG] 특정 문서 전체 검색: {len(doc_chunks)}개 파일 병합, 총 {len(chunks)}개 청크 발견")
                            else:
                                target_filename = list(doc_chunks.keys())[0]
                                specific_doc_filename = target_filename
                                print(f"[RAG] 특정 문서 전체 검색: {target_filename}, {len(chunks)}개 청크 발견")
                        else:
                            # 날짜나 문서 유형 중 하나만 지정된 경우, 가장 많은 청크를 가진 문서 선택
                            target_filename = max(doc_chunks.keys(), key=lambda f: len(doc_chunks[f]))
                            chunks = doc_chunks[target_filename]
                            specific_doc_filename = target_filename
                            print(f"[RAG] 특정 문서 전체 검색: {target_filename}, {len(chunks)}개 청크 발견")
                        
                        # 페이지 순서대로 컨텍스트 구성
                        contexts = []
                        sources = []
                        
                        for chunk in chunks:
                            page = chunk["page"]
                            text = chunk["text"]
                            metadata = chunk["metadata"]
                            
                            # 메타데이터 정보 추출
                            filename = metadata.get("filename", "알 수 없음")
                            doc_type = metadata.get("doc_type")
                            doc_title = metadata.get("doc_title")
                            date = metadata.get("date")
                            
                            # 컨텍스트에 메타데이터 정보 포함
                            metadata_str = f"[문서 정보]\n"
                            metadata_str += f"- 파일명: {filename}\n"
                            metadata_str += f"- 페이지: {page}\n"
                            if date:
                                metadata_str += f"- 날짜: {date}\n"
                            if doc_type:
                                metadata_str += f"- 문서 유형: {doc_type}\n"
                            if doc_title:
                                metadata_str += f"- 문서 제목: {doc_title}\n"
                            metadata_str += f"\n[문서 내용]\n{text}"
                            
                            contexts.append(metadata_str)
                            sources.append({
                                "filename": filename,
                                "page": page,
                                "type": metadata.get("type", "text"),
                                "text": text[:200] + "..." if len(text) > 200 else text
                            })
                        
                        context_text = "\n\n---\n\n".join(contexts)
                        
                        # LLM 프롬프트 구성
                        user_prompt = f"""다음은 특정 문서의 전체 내용입니다. 페이지 순서대로 제공되었습니다.

[문서 전체 내용]
{context_text}

[질문]
{query_text}

**중요 지침:**

1. **메타데이터 활용 필수**
   - 각 문서 청크에는 파일명, 페이지, 날짜, 문서 유형, 문서 제목 등의 메타데이터가 포함되어 있습니다.
   - 이 메타데이터 정보를 반드시 활용하여 답변하세요.
   - 질문에서 언급한 날짜, 문서 유형, 파일명과 메타데이터가 일치하는지 확인하세요.

2. **페이지 순서 고려**
   - 문서는 페이지 순서대로 제공되었습니다.
   - 페이지 순서를 고려하여 답변하세요.

3. **컨텍스트 기반 답변**
   - 위 문서의 전체 내용을 참고하여 질문에 답변하세요.
   - 문서에 없는 내용은 절대 답변하지 마세요.

4. **소스 명시**
   - 답변 마지막에 [출처: 파일명, 페이지 X] 형식으로 소스를 명시하세요.
   - 여러 페이지에서 정보를 가져왔다면 모든 페이지를 명시하세요."""
                        
                        # Ollama로 답변 생성
                        try:
                            import os
                            if "http://" in self.ollama_base_url or "https://" in self.ollama_base_url:
                                host = self.ollama_base_url.replace("http://", "").replace("https://", "")
                            else:
                                host = self.ollama_base_url
                            
                            client = ollama.Client(host=host)
                            
                            print(f"[RAG] Ollama 연결 시도: {host}, 모델: {self.ollama_model}")
                            
                            llm_start = time.time()
                            response = client.chat(
                                model=self.ollama_model,
                                messages=[
                                    {"role": "system", "content": self.system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                options={
                                    "temperature": 0.1,
                                    "top_p": 0.9,
                                    "num_predict": 2000  # 전체 문서이므로 더 긴 답변 허용
                                }
                            )
                            llm_time = time.time() - llm_start
                            
                            answer = response["message"]["content"]
                            print(f"[RAG] Ollama 응답 받음 (길이: {len(answer)}자, 소요 시간: {llm_time:.2f}초)")
                            
                            has_answer = "지식 베이스에 없는 내용" not in answer and "관련 문서가 없습니다" not in answer
                            
                            if len(answer.strip()) < 10:
                                has_answer = False
                                answer = "지식 베이스에 없는 내용입니다"
                            
                            total_time = time.time() - total_start
                            print(f"[RAG] 특정 문서 전체 검색 완료 (총 {total_time:.2f}초)")
                            
                            return {
                                "answer": answer,
                                "sources": sources,
                                "has_answer": has_answer
                            }
                        except Exception as e:
                            import traceback
                            error_detail = traceback.format_exc()
                            print(f"[RAG] Ollama 오류:")
                            print(error_detail)
                            
                            if "Connection" in str(e) or "refused" in str(e).lower() or "timeout" in str(e).lower():
                                answer = "⚠️ Ollama 서버에 연결할 수 없습니다.\n\nOllama가 실행 중인지 확인하세요:\n  ollama serve"
                            elif "model" in str(e).lower() or "not found" in str(e).lower():
                                answer = f"⚠️ Ollama 모델을 찾을 수 없습니다.\n\n다음 명령어로 모델을 다운로드하세요:\n  ollama pull {self.ollama_model}"
                            else:
                                answer = f"⚠️ 답변 생성 중 오류가 발생했습니다.\n\n오류: {str(e)[:200]}"
                            
                            return {
                                "answer": answer,
                                "sources": sources,
                                "has_answer": False
                            }
                else:
                    print(f"[RAG] 특정 문서를 찾을 수 없음: 날짜={specific_doc_date}, 문서유형={doc_type_mentioned}")
            except Exception as e:
                import traceback
                print(f"[RAG] 특정 문서 전체 검색 오류: {e}")
                traceback.print_exc()
        
        try:
            print(f"[RAG] 쿼리 처리 시작: {query_text[:50]}...")
            
            # 쿼리 임베딩 생성 (CPU)
            embed_start = time.time()
            query_embedding = self.embedding_model.encode(
                query_text,
                normalize_embeddings=True
            ).tolist()
            embed_time = time.time() - embed_start
            print(f"[RAG] 임베딩 생성 완료 ({embed_time:.2f}초)")
            
            # 컬렉션의 문서 수 확인하여 n_results 조정
            search_start = time.time()
            try:
                collection_count = self.collection.count()
                n_results = min(TOP_K_RESULTS, max(1, collection_count))
                print(f"[RAG] 컬렉션 문서 수: {collection_count}, 요청 결과 수: {n_results}")
            except Exception as e:
                print(f"[RAG] 컬렉션 카운트 오류: {e}, 기본값 사용")
                n_results = TOP_K_RESULTS
            
            # 필터링 조건 설정 (파일명 우선, 그 다음 날짜+문서유형, 그 다음 문서 유형만)
            where_filter = None
            if specific_filename:
                # 특정 파일명이 감지된 경우 해당 파일만 검색
                where_filter = {"filename": specific_filename}
                print(f"[RAG] 파일명 필터링 적용: {specific_filename}")
            elif specific_doc_date and doc_type_mentioned:
                # 날짜와 문서 유형이 모두 감지된 경우 둘 다 필터링 (ChromaDB 형식: $and 연산자 사용)
                where_filter = {
                    "$and": [
                        {"date": specific_doc_date},
                        {"doc_type": doc_type_mentioned}
                    ]
                }
                print(f"[RAG] 날짜+문서유형 필터링 적용: 날짜={specific_doc_date}, 유형={doc_type_mentioned}")
            elif specific_doc_date:
                # 날짜만 감지된 경우 날짜 필터링
                where_filter = {"date": specific_doc_date}
                print(f"[RAG] 날짜 필터링 적용: {specific_doc_date}")
            elif doc_type_mentioned:
                # 문서 유형 필터링
                where_filter = {"doc_type": doc_type_mentioned}
                print(f"[RAG] 문서 유형 필터링 적용: {doc_type_mentioned}")
            
            # 유사 문서 검색
            if where_filter:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_filter
                )
            else:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
            search_time = time.time() - search_start
            print(f"[RAG] 벡터 검색 완료 ({search_time:.2f}초)")
            
            if not results["ids"] or not results["ids"][0]:
                print(f"[RAG] 검색 결과 없음")
                return {
                    "answer": "지식 베이스에 관련 문서가 없습니다.",
                    "sources": [],
                    "has_answer": False
                }
            
            print(f"[RAG] 검색 결과: {len(results['ids'][0])}개 문서 발견")
        except Exception as e:
            import traceback
            print(f"[RAG] ChromaDB 쿼리 오류:")
            print(traceback.format_exc())
            return {
                "answer": f"문서 검색 중 오류가 발생했습니다: {str(e)}",
                "sources": [],
                "has_answer": False
            }
        
        # 문서 목록/제목 질문인 경우 메타데이터에서 직접 제목 조회
        if (is_title_query or is_list_query) and (doc_type_mentioned or keyword):
            try:
                # 필터 조건 설정
                where_filter = {}
                if doc_type_mentioned:
                    where_filter["doc_type"] = doc_type_mentioned
                
                # 해당 조건의 모든 문서 가져오기
                if where_filter:
                    all_results = self.collection.get(where=where_filter)
                else:
                    all_results = self.collection.get()
                
                if all_results["metadatas"]:
                    # 고유한 문서 제목 추출 (filename 기준)
                    unique_titles = {}
                    for metadata in all_results["metadatas"]:
                        doc_title = metadata.get("doc_title")
                        filename = metadata.get("filename")
                        doc_type = metadata.get("doc_type")
                        
                        # 키워드 필터링 (키워드가 있으면 문서 제목이나 파일명에 포함되는지 확인)
                        if keyword:
                            keyword_lower = keyword.lower()
                            title_match = doc_title and keyword_lower in doc_title.lower()
                            filename_match = filename and keyword_lower in filename.lower()
                            if not title_match and not filename_match:
                                continue  # 키워드가 없으면 제외
                        
                        if doc_title and filename:
                            if filename not in unique_titles:
                                unique_titles[filename] = {
                                    "title": doc_title,
                                    "date": metadata.get("date"),
                                    "filename": filename,
                                    "doc_type": doc_type
                                }
                    
                    if unique_titles:
                        # 문서 제목만으로 답변 생성
                        if keyword:
                            answer_prefix = f"{keyword.upper()}와 관련된 문서는 총 {len(unique_titles)}개입니다:\n\n"
                        elif doc_type_mentioned:
                            answer_prefix = f"{doc_type_mentioned}의 모든 문서 제목은 다음과 같습니다:\n\n"
                        else:
                            answer_prefix = f"관련 문서는 총 {len(unique_titles)}개입니다:\n\n"
                        
                        title_list = "\n".join([f"{i+1}. {info['title']}" for i, info in enumerate(unique_titles.values())])
                        answer = answer_prefix + title_list
                        
                        # 출처는 해당 문서들의 첫 페이지 (원본 파일명 사용)
                        sources = []
                        for filename, info in unique_titles.items():
                            # 해당 파일의 첫 페이지 찾기
                            file_results = self.collection.get(where={"filename": filename})
                            if file_results["metadatas"]:
                                first_page = min([m.get("page", 1) for m in file_results["metadatas"]])
                                sources.append({
                                    "filename": filename,  # 원본 파일명 사용
                                    "page": first_page,
                                    "type": "text",
                                    "text": f"{info['title']}"
                                })
                        
                        total_time = time.time() - total_start
                        print(f"[RAG] 문서 목록 조회 완료: {len(unique_titles)}개 문서 (총 {total_time:.2f}초)")
                        
                        return {
                            "answer": answer,
                            "sources": sources,
                            "has_answer": True
                        }
            except Exception as e:
                import traceback
                print(f"[RAG] 문서 목록 조회 오류: {e}")
                traceback.print_exc()
        
        # 컨텍스트 구성 (파일명 필터링 적용 - 이중 안전장치)
        # 먼저 파일명별로 그룹화
        filename_groups = {}  # {filename: [chunks]}
        filtered_count = 0
        
        for i, doc_id in enumerate(results["ids"][0]):
            doc_text = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            result_filename = metadata.get("filename")
            
            # 파일명 필터링: 특정 파일명이 감지되었고, 검색 결과의 파일명이 일치하지 않으면 제외
            if specific_filename and result_filename != specific_filename:
                filtered_count += 1
                print(f"[RAG] 파일명 필터링: '{result_filename}' 제외 (요청된 파일: '{specific_filename}')")
                continue
            
            # 감지된 파일명 목록이 있고, 현재 파일명이 목록에 없으면 제외
            if detected_filenames and result_filename not in detected_filenames:
                filtered_count += 1
                print(f"[RAG] 파일명 필터링: '{result_filename}' 제외 (감지된 파일 목록에 없음)")
                continue
            
            # 파일명별로 그룹화
            if result_filename not in filename_groups:
                filename_groups[result_filename] = []
            
            filename_groups[result_filename].append({
                "doc_text": doc_text,
                "metadata": metadata,
                "index": i  # 원본 순서 유지용
            })
        
        # 각 파일명당 하나의 대표 청크만 선택 (페이지 번호가 가장 작은 청크 또는 첫 번째 청크)
        # 파일명 기반 정렬을 위해 먼저 파일명으로 정렬
        sorted_filename_groups = sorted(filename_groups.items(), key=lambda x: x[0] if x[0] else '')
        
        contexts = []
        sources = []
        unique_filenames = set()
        
        for filename, chunks in sorted_filename_groups:
            if not chunks:
                continue
            
            # 페이지 번호가 있는 경우 가장 작은 페이지의 청크 선택, 없으면 첫 번째 청크 선택
            best_chunk = None
            min_page = float('inf')
            
            for chunk in chunks:
                page = chunk["metadata"].get("page")
                if page is not None:
                    try:
                        page_num = int(page) if isinstance(page, (int, float, str)) and str(page).isdigit() else float('inf')
                        if page_num < min_page:
                            min_page = page_num
                            best_chunk = chunk
                    except:
                        pass
            
            # 페이지 번호가 없거나 파싱 실패한 경우 첫 번째 청크 선택
            if best_chunk is None:
                best_chunk = chunks[0]
            
            # 선택된 청크의 메타데이터 정보 추출
            metadata = best_chunk["metadata"]
            doc_text = best_chunk["doc_text"]
            filename = metadata.get("filename", "알 수 없음")
            page = metadata.get("page", "알 수 없음")
            doc_type = metadata.get("doc_type")
            doc_title = metadata.get("doc_title")
            date = metadata.get("date")
            
            # 중복 제거: 이미 추가된 파일명이면 건너뛰기
            if filename in unique_filenames:
                continue
            
            unique_filenames.add(filename)
            
            # 컨텍스트에 메타데이터 정보 포함
            metadata_str = f"[문서 정보]\n"
            metadata_str += f"- 파일명: {filename}\n"
            metadata_str += f"- 페이지: {page}\n"
            if date:
                metadata_str += f"- 날짜: {date}\n"
            if doc_type:
                metadata_str += f"- 문서 유형: {doc_type}\n"
            if doc_title:
                metadata_str += f"- 문서 제목: {doc_title}\n"
            metadata_str += f"\n[문서 내용]\n{doc_text}"
            
            contexts.append(metadata_str)
            sources.append({
                "filename": filename,
                "page": page,
                "type": metadata.get("type", "text"),
                "text": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
            })
        
        if filtered_count > 0:
            print(f"[RAG] 파일명 필터링 완료: {filtered_count}개 청크 제외")
        
        duplicate_removed = sum(len(chunks) - 1 for chunks in filename_groups.values() if len(chunks) > 1)
        if duplicate_removed > 0:
            print(f"[RAG] 파일명 중복 제거 완료: {duplicate_removed}개 중복 청크 제외, {len(contexts)}개 유니크 파일 사용")
        
        if not contexts:
            print(f"[RAG] 경고: 파일명 필터링 후 사용 가능한 청크가 없음")
            return {
                "answer": f"요청하신 파일명('{specific_filename if specific_filename else '알 수 없음'}')과 일치하는 문서를 찾을 수 없습니다.",
                "sources": [],
                "has_answer": False
            }
        
        context_text = "\n\n---\n\n".join(contexts)
        
        # 문서 유형별 개수 정보 및 제목 정보 추가
        metadata_info = ""
        if doc_titles_info:
            # 문서 제목 질문인 경우 제목 정보 우선 제공
            metadata_info = doc_titles_info
        elif doc_type_info:
            metadata_info = f"\n\n[문서 유형별 개수 정보]\n{doc_type_info}\n"
        elif is_count_query and all_doc_types:
            # 모든 문서 유형 개수 정보 제공
            type_list = "\n".join([f"- {doc_type}: {count}개" for doc_type, count in sorted(all_doc_types.items())])
            metadata_info = f"\n\n[문서 유형별 개수 정보]\n{type_list}\n"
        
        # LLM 프롬프트 구성
        user_prompt = f"""다음 컨텍스트를 참고하여 질문에 답변하세요.

[컨텍스트]
{context_text}{metadata_info}

[질문]
{query_text}

**중요 지침:**

1. **메타데이터 활용 필수**
   - 각 문서 청크에는 파일명, 페이지, 날짜, 문서 유형, 문서 제목 등의 메타데이터가 포함되어 있습니다.
   - 이 메타데이터 정보를 반드시 활용하여 답변하세요.
   - 예를 들어, 특정 날짜나 문서 유형을 언급한 질문이면 해당 메타데이터와 일치하는 문서만 참고하세요.

2. **파일명 필터링**
   - 질문에서 특정 파일명을 언급했다면, 해당 파일명과 일치하는 문서만 사용하세요.
   - 다른 파일명의 문서는 무시하세요.

3. **날짜 및 문서 유형 필터링**
   - 질문에서 날짜(예: "250211")나 문서 유형(예: "재직증명서")을 언급했다면, 해당 메타데이터와 일치하는 문서만 사용하세요.

4. **컨텍스트 기반 답변**
   - 위 컨텍스트에 없는 내용은 절대 답변하지 마세요.
   - 문서 유형별 개수 정보가 제공된 경우, 해당 정보를 정확히 사용하여 답변하세요.

5. **소스 명시**
   - 답변 마지막에 [출처: 파일명, 페이지 X] 형식으로 소스를 명시하세요.
   - 여러 소스가 있으면 모두 명시하세요."""
        
        # Ollama로 답변 생성 (GPU)
        try:
            # Ollama 클라이언트가 base_url을 사용하도록 설정
            import os
            # 환경 변수 설정
            if "http://" in self.ollama_base_url or "https://" in self.ollama_base_url:
                host = self.ollama_base_url.replace("http://", "").replace("https://", "")
            else:
                host = self.ollama_base_url
            
            client = ollama.Client(host=host)
            
            print(f"[RAG] Ollama 연결 시도: {host}, 모델: {self.ollama_model}")
            
            # LLM 추론 시간 측정
            llm_start = time.time()
            response = client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            )
            llm_time = time.time() - llm_start
            
            answer = response["message"]["content"]
            print(f"[RAG] Ollama 응답 받음 (길이: {len(answer)}자, 소요 시간: {llm_time:.2f}초)")
            
            # 성능 분석
            if llm_time > 10:
                print(f"⚠️ 경고: LLM 응답이 매우 느립니다 ({llm_time:.2f}초)")
                print(f"   GPU가 제대로 사용되고 있는지 확인하세요.")
            elif llm_time > 5:
                print(f"⚠️ 주의: LLM 응답이 다소 느립니다 ({llm_time:.2f}초)")
            
            # 답변 검증
            has_answer = "지식 베이스에 없는 내용" not in answer and "관련 문서가 없습니다" not in answer
            
            if len(answer.strip()) < 10:
                has_answer = False
                answer = "지식 베이스에 없는 내용입니다"
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[RAG] Ollama 오류:")
            print(error_detail)
            
            # 친절한 에러 메시지
            if "Connection" in str(e) or "refused" in str(e).lower() or "timeout" in str(e).lower():
                answer = "⚠️ Ollama 서버에 연결할 수 없습니다.\n\nOllama가 실행 중인지 확인하세요:\n  ollama serve\n\n또는 모델이 다운로드되었는지 확인:\n  ollama list"
            elif "model" in str(e).lower() or "not found" in str(e).lower():
                answer = f"⚠️ Ollama 모델을 찾을 수 없습니다.\n\n다음 명령어로 모델을 다운로드하세요:\n  ollama pull {self.ollama_model}"
            else:
                answer = f"⚠️ 답변 생성 중 오류가 발생했습니다.\n\n오류: {str(e)[:200]}"
            has_answer = False
        
        total_time = time.time() - total_start
        print(f"[RAG] 전체 쿼리 처리 완료 (총 {total_time:.2f}초)")
        
        return {
            "answer": answer,
            "sources": sources,
            "has_answer": has_answer
        }
    
    def delete_document(self, file_id: str):
        """벡터 DB에서 문서 삭제 (file_id로 직접 삭제)"""
        try:
            existing = self.collection.get(where={"file_id": file_id})
            if existing["ids"]:
                deleted_count = len(existing["ids"])
                self.collection.delete(ids=existing["ids"])
                print(f"[RAG] 문서 삭제 완료: file_id={file_id}, 삭제된 청크 수={deleted_count}")
                return deleted_count
            else:
                print(f"[RAG] 삭제할 문서를 찾을 수 없음: file_id={file_id}")
                return 0
        except Exception as e:
            print(f"[RAG] 문서 삭제 오류: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def delete_document_by_path(self, file_path: Path):
        """벡터 DB에서 문서 삭제 (파일 경로 기반)"""
        try:
            # 파일 경로 기반으로 file_id 생성
            file_id = self._get_file_id(file_path)
            print(f"[RAG] 파일 경로 기반 삭제 시도: {file_path}, file_id={file_id}")
            
            # file_id로 문서 검색 및 삭제
            existing = self.collection.get(where={"file_id": file_id})
            if existing["ids"]:
                deleted_count = len(existing["ids"])
                self.collection.delete(ids=existing["ids"])
                print(f"[RAG] 문서 삭제 완료: file_id={file_id}, 삭제된 청크 수={deleted_count}")
                return deleted_count
            else:
                # file_id로 찾지 못하면 filename으로도 시도
                filename = file_path.name
                print(f"[RAG] file_id로 찾지 못함, filename으로 재시도: {filename}")
                existing = self.collection.get(where={"filename": filename})
                if existing["ids"]:
                    deleted_count = len(existing["ids"])
                    self.collection.delete(ids=existing["ids"])
                    print(f"[RAG] 문서 삭제 완료 (filename 기반): filename={filename}, 삭제된 청크 수={deleted_count}")
                    return deleted_count
                else:
                    print(f"[RAG] 삭제할 문서를 찾을 수 없음: file_path={file_path}, file_id={file_id}, filename={filename}")
                    return 0
        except Exception as e:
            print(f"[RAG] 문서 삭제 오류: {e}")
            import traceback
            traceback.print_exc()
            return 0


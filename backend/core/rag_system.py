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
        
        # 시스템 프롬프트 (간소화 + 중복 처리)
        self.system_prompt = """너는 기업 문서 검색 어시스턴트다.

규칙:
1. 제공된 컨텍스트만 사용하여 답변한다. 없는 정보는 "해당 정보가 없습니다"라고 답한다.
2. 동일한 문서 제목, 참석자 명단, 항목이 여러 번 나오면 한 번만 요약하여 출력한다.
3. 마크다운을 사용하지 않고 순수 텍스트로 답변한다.
4. 답변 끝에 [출처: 파일명, 페이지] 형식으로 출처를 표기한다."""
    
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
        
        print(f"\n{'='*60}")
        print(f"[INDEX] 문서 인덱싱 시작: {filename}")
        print(f"{'='*60}")
        
        # 문서 처리 (Layout-aware)
        print(f"[INDEX] 1단계: 문서 파싱 중...")
        chunks = self.doc_processor.extract_text_with_layout(file_path)
        
        # 표 관련 통계 로그
        table_chunks = [c for c in chunks if c.get("type") == "table"]
        text_chunks = [c for c in chunks if c.get("type") == "text"]
        print(f"\n[INDEX] 파싱 결과:")
        print(f"    - 총 청크 수: {len(chunks)}")
        print(f"    - 텍스트 청크: {len(text_chunks)}개")
        print(f"    - 표 청크: {len(table_chunks)}개")
        
        # 표 청크 상세 정보 출력
        if table_chunks:
            print(f"\n[INDEX] 감지된 표 상세 정보:")
            for i, tc in enumerate(table_chunks):
                page = tc.get("page", "?")
                text_preview = tc.get("text", "")[:200].replace('\n', ' ')
                print(f"    표 {i+1} (페이지 {page}): {text_preview}...")
        
        # 기존 문서 청크 삭제 (같은 파일 재업로드 시)
        try:
            existing = self.collection.get(where={"file_id": file_id})
            if existing["ids"]:
                print(f"[INDEX] 기존 청크 {len(existing['ids'])}개 삭제")
                self.collection.delete(ids=existing["ids"])
        except:
            pass
        
        # 임베딩 생성 (CPU)
        print(f"\n[INDEX] 2단계: 임베딩 생성 중... ({len(chunks)}개 청크)")
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
            
            # 청크 메타데이터 추출 (document_processor에서 온 정보)
            chunk_metadata = chunk.get("metadata", {})
            has_table = chunk_metadata.get("has_table", False)
            table_continued = chunk_metadata.get("table_continued", False)
            
            # 기본 메타데이터
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "page": chunk["page"],
                "type": chunk["type"],
                "chunk_index": i,
                "has_table": has_table,
                "table_continued": table_continued
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
        print(f"\n[INDEX] 3단계: 벡터 DB 저장 중...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        # 저장된 표 청크 메타데이터 출력
        saved_table_count = sum(1 for m in metadatas if m.get("type") == "table")
        print(f"\n[INDEX] 저장 완료!")
        print(f"    - 총 저장된 청크: {len(chunks)}개")
        print(f"    - 표 청크 메타데이터:")
        for i, m in enumerate(metadatas):
            if m.get("type") == "table":
                print(f"        페이지 {m.get('page')}: has_table={m.get('has_table', False)}, type={m.get('type')}")
        
        print(f"{'='*60}\n")
        
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
    
    def _classify_intent(self, query_text: str) -> str:
        """
        LLM 기반 Intent Classifier (가벼운 프롬프트 사용)
        
        Returns:
            "GLOBAL" - 전체 목록/개수 조회 (벡터 검색 생략)
            "DETAIL" - 특정 내용 분석 (하이브리드 검색)
        """
        # 1단계: 빠른 규칙 기반 분류 (LLM 호출 최소화)
        import re
        
        # GLOBAL 패턴 (명확한 경우만)
        global_patterns = [
            r"몇\s*(개|건)",           # "몇 개", "몇 건"
            r"총\s*(몇|개|건|\d)",     # "총 몇개", "총 5개"
            r"(등록|저장)된.*(문서|파일)",  # "등록된 문서"
            r"(모든|전체).*(파일|문서).*목록",  # "모든 파일 목록"
            r"(파일|문서)\s*목록",     # "파일 목록"
            r"어떤\s*(문서|파일)",     # "어떤 문서가 있어"
        ]
        
        for pattern in global_patterns:
            if re.search(pattern, query_text):
                print(f"[Intent] 규칙 기반 분류: GLOBAL (패턴: {pattern})")
                return "GLOBAL"
        
        # DETAIL 패턴 (명확한 경우)
        detail_patterns = [
            r"\d{6}",                  # 날짜 코드 (예: 251111)
            r"(내용|정보|기준|항목|금액|이름|성명)",  # 세부 정보 요청
            r"(설명|분석|알려|말해).*줘",  # 분석 요청
        ]
        
        for pattern in detail_patterns:
            if re.search(pattern, query_text):
                print(f"[Intent] 규칙 기반 분류: DETAIL (패턴: {pattern})")
                return "DETAIL"
        
        # 2단계: 애매한 경우 LLM으로 분류
        try:
            if "http://" in self.ollama_base_url or "https://" in self.ollama_base_url:
                host = self.ollama_base_url.replace("http://", "").replace("https://", "")
            else:
                host = self.ollama_base_url
            
            client = ollama.Client(host=host)
            
            classify_prompt = f"""질문을 분류하세요. 한 단어로만 답하세요.

GLOBAL: 문서 개수, 목록, 현황 질문
DETAIL: 문서 내용, 세부 정보 질문

질문: {query_text}
분류:"""
            
            response = client.chat(
                model=self.ollama_model,
                messages=[{"role": "user", "content": classify_prompt}],
                options={"temperature": 0, "num_predict": 10}
            )
            
            result = response.message.content.strip().upper()
            
            if "GLOBAL" in result:
                print(f"[Intent] LLM 분류: GLOBAL")
                return "GLOBAL"
            else:
                print(f"[Intent] LLM 분류: DETAIL")
                return "DETAIL"
                
        except Exception as e:
            print(f"[Intent] LLM 분류 실패, 기본값 DETAIL 사용: {e}")
            return "DETAIL"
    
    def _handle_global_query(self, query_text: str, doc_type_mentioned: str = None) -> Dict:
        """
        GLOBAL Intent: 전체 현황 파악 (벡터 검색 생략, 메타데이터만 사용)
        
        LLM에게 파일 리스트를 전달하고 사실 기반 응답 생성
        """
        print(f"[RAG] GLOBAL 모드: 메타데이터 기반 응답")
        
        try:
            # 모든 문서 메타데이터 수집
            all_docs = self.collection.get()
            
            if not all_docs["metadatas"]:
                return {
                    "answer": "현재 등록된 문서가 없습니다.",
                    "sources": [],
                    "has_answer": True,
                    "intent": "GLOBAL"
                }
            
            # 유니크 파일 정보 추출
            file_info = {}
            for metadata in all_docs["metadatas"]:
                filename = metadata.get("filename")
                if not filename:
                    continue
                
                if filename not in file_info:
                    file_info[filename] = {
                        "doc_type": metadata.get("doc_type", ""),
                        "date": metadata.get("date", ""),
                        "page_count": 0
                    }
                file_info[filename]["page_count"] += 1
            
            # 문서 유형별 그룹화
            doc_type_groups = {}
            for filename, info in file_info.items():
                dt = info["doc_type"] or "(유형 없음)"
                if dt not in doc_type_groups:
                    doc_type_groups[dt] = []
                doc_type_groups[dt].append(filename)
            
            # 파일 리스트 컨텍스트 생성
            file_list_context = f"[등록된 문서 현황]\n총 문서 수: {len(file_info)}개\n\n"
            
            file_list_context += "[문서 유형별 현황]\n"
            for dt, files in sorted(doc_type_groups.items()):
                file_list_context += f"- {dt}: {len(files)}개\n"
            
            file_list_context += "\n[전체 파일 목록]\n"
            for filename in sorted(file_info.keys()):
                info = file_info[filename]
                dt = info["doc_type"] or "(유형 없음)"
                file_list_context += f"- {filename} (유형: {dt})\n"
            
            # LLM에게 파일 리스트 기반 응답 요청
            try:
                if "http://" in self.ollama_base_url or "https://" in self.ollama_base_url:
                    host = self.ollama_base_url.replace("http://", "").replace("https://", "")
                else:
                    host = self.ollama_base_url
                
                client = ollama.Client(host=host)
                
                user_prompt = f"""다음은 현재 등록된 문서 목록입니다.

{file_list_context}

질문: {query_text}

위 목록을 바탕으로 정확하게 답변하세요. 마크다운을 사용하지 마세요."""
                
                response = client.chat(
                    model=self.ollama_model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    options={
                        "temperature": 0.1,
                        "num_predict": 1000
                    }
                )
                
                answer = response.message.content
                
            except Exception as e:
                # LLM 실패 시 직접 응답 생성
                print(f"[RAG] GLOBAL LLM 응답 실패, 직접 생성: {e}")
                
                if doc_type_mentioned and doc_type_mentioned in doc_type_groups:
                    count = len(doc_type_groups[doc_type_mentioned])
                    answer = f"{doc_type_mentioned} 문서는 총 {count}개입니다."
                    if count <= 10:
                        answer += "\n\n파일 목록:\n" + "\n".join([f"- {f}" for f in doc_type_groups[doc_type_mentioned]])
                else:
                    answer = f"등록된 문서는 총 {len(file_info)}개입니다.\n\n"
                    answer += "문서 유형별 현황:\n"
                    for dt, files in sorted(doc_type_groups.items()):
                        answer += f"- {dt}: {len(files)}개\n"
            
            return {
                "answer": answer,
                "sources": [{"filename": f, "page": 1, "type": "metadata"} for f in list(file_info.keys())[:5]],
                "has_answer": True,
                "intent": "GLOBAL"
            }
            
        except Exception as e:
            print(f"[RAG] GLOBAL 처리 오류: {e}")
            import traceback
            traceback.print_exc()
            return {
                "answer": f"문서 현황 조회 중 오류가 발생했습니다: {str(e)}",
                "sources": [],
                "has_answer": False,
                "intent": "GLOBAL"
            }
    
    def query(self, query_text: str) -> Dict:
        """RAG 질의 처리 (Intent 기반 동적 검색 전략)"""
        import time
        import re
        total_start = time.time()
        
        print(f"[RAG] 쿼리 수신: {query_text}")
        
        # ========== Intent Classification ==========
        intent = self._classify_intent(query_text)
        
        # 문서 유형 감지
        doc_type_mentioned = None
        all_doc_types = self.get_all_document_types()
        for doc_type in all_doc_types.keys():
            if doc_type in query_text:
                doc_type_mentioned = doc_type
                print(f"[RAG] 문서 유형 감지: {doc_type}")
                break
        
        # ========== GLOBAL Intent: 메타데이터 기반 응답 ==========
        if intent == "GLOBAL":
            return self._handle_global_query(query_text, doc_type_mentioned)
        
        # ========== DETAIL Intent: 하이브리드 검색 ==========
        print(f"[RAG] DETAIL 모드: 하이브리드 검색 실행")
        
        # 기존 변수 초기화
        doc_type_info = None
        doc_titles_info = None
        if doc_type_mentioned:
            doc_type_info = f"{doc_type_mentioned} 문서는 총 {all_doc_types[doc_type_mentioned]}개입니다."
        
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
                                    "top_p": 0.85,
                                    "num_predict": 2000,
                                    "repeat_penalty": 1.2  # 반복 답변 방지
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
        
        # [컨텍스트 확장] 모든 청크를 페이지 순으로 정렬하여 LLM에 전달
        # 파일명별로 그룹화된 청크들을 풀어서 하나의 리스트로 만듦
        all_chunks = []
        for filename, chunks in filename_groups.items():
            for chunk in chunks:
                chunk["_sort_filename"] = filename or ""
                # 페이지 번호 파싱
                page = chunk["metadata"].get("page", 0)
                try:
                    chunk["_sort_page"] = int(page) if str(page).isdigit() else 0
                except:
                    chunk["_sort_page"] = 0
                all_chunks.append(chunk)
        
        # 파일명 → 페이지 순으로 정렬
        all_chunks.sort(key=lambda x: (x["_sort_filename"], x["_sort_page"]))
        
        # ========== De-duplication 강화 ==========
        def calculate_text_similarity(text1: str, text2: str) -> float:
            """텍스트 유사도 계산 (간단한 Jaccard 유사도)"""
            if not text1 or not text2:
                return 0.0
            # 단어 단위로 분할
            words1 = set(text1.split())
            words2 = set(text2.split())
            if not words1 or not words2:
                return 0.0
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0
        
        # 1단계: 파일명+페이지 기반 중복 제거
        seen_file_page = set()
        dedup_chunks_stage1 = []
        for chunk in all_chunks:
            key = (chunk["_sort_filename"], chunk["_sort_page"])
            if key not in seen_file_page:
                seen_file_page.add(key)
                dedup_chunks_stage1.append(chunk)
        
        stage1_removed = len(all_chunks) - len(dedup_chunks_stage1)
        if stage1_removed > 0:
            print(f"[De-dup] 파일명+페이지 중복 제거: {stage1_removed}개 제거")
        
        # 2단계: 텍스트 유사도 기반 중복 제거 (90% 이상 유사)
        SIMILARITY_THRESHOLD = 0.9
        dedup_chunks_stage2 = []
        
        for chunk in dedup_chunks_stage1:
            is_duplicate = False
            chunk_text = chunk["doc_text"]
            
            for existing_chunk in dedup_chunks_stage2:
                existing_text = existing_chunk["doc_text"]
                similarity = calculate_text_similarity(chunk_text, existing_text)
                
                if similarity >= SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    # 기존 청크에 페이지 정보 병합 (참조용)
                    if "_merged_pages" not in existing_chunk:
                        existing_chunk["_merged_pages"] = [existing_chunk["_sort_page"]]
                    existing_chunk["_merged_pages"].append(chunk["_sort_page"])
                    break
            
            if not is_duplicate:
                dedup_chunks_stage2.append(chunk)
        
        stage2_removed = len(dedup_chunks_stage1) - len(dedup_chunks_stage2)
        if stage2_removed > 0:
            print(f"[De-dup] 텍스트 유사도 중복 제거: {stage2_removed}개 제거 (유사도 {SIMILARITY_THRESHOLD*100:.0f}% 이상)")
        
        # 최소 15개, 최대 30개 청크 선택
        MIN_CHUNKS = 15
        MAX_CHUNKS = 30
        selected_chunks = dedup_chunks_stage2[:MAX_CHUNKS]
        
        # 청크가 부족하면 있는 만큼만 사용
        if len(selected_chunks) < MIN_CHUNKS:
            print(f"[RAG] 경고: 검색된 청크({len(selected_chunks)}개)가 최소 요구치({MIN_CHUNKS}개)보다 적음")
        
        print(f"[De-dup] 최종 청크 수: {len(selected_chunks)}개 (원본 {len(all_chunks)}개)")
        
        contexts = []
        sources = []
        unique_filenames = set()
        
        for chunk in selected_chunks:
            metadata = chunk["metadata"]
            doc_text = chunk["doc_text"]
            filename = metadata.get("filename", "알 수 없음")
            page = metadata.get("page", "알 수 없음")
            doc_type = metadata.get("doc_type")
            doc_title = metadata.get("doc_title")
            date = metadata.get("date")
            
            unique_filenames.add(filename)  # 통계용
            
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
        
        print(f"[RAG] 컨텍스트 구성 완료: {len(contexts)}개 청크, {len(unique_filenames)}개 파일에서 추출")
        
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
                    "top_p": 0.85,
                    "num_predict": 1500,
                    "repeat_penalty": 1.2  # 반복 답변 방지
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
    
    def delete_document_by_filename(self, filename: str):
        """벡터 DB에서 문서 삭제 (원본 파일명 기반)"""
        try:
            if not filename:
                print(f"[RAG] 삭제 실패: 파일명이 비어있음")
                return 0
            
            print(f"[RAG] 파일명 기반 삭제 시도: {filename}")
            
            # 정확한 파일명 매칭
            existing = self.collection.get(where={"filename": filename})
            
            if existing["ids"]:
                deleted_count = len(existing["ids"])
                self.collection.delete(ids=existing["ids"])
                print(f"[RAG] 문서 삭제 완료 (filename): {filename}, 삭제된 청크 수={deleted_count}")
                return deleted_count
            else:
                # 부분 매칭 시도 (안전한 파일명으로 저장된 경우)
                print(f"[RAG] 정확한 매칭 실패, 전체 검색으로 재시도")
                all_docs = self.collection.get()
                
                ids_to_delete = []
                for i, metadata in enumerate(all_docs["metadatas"]):
                    doc_filename = metadata.get("filename", "")
                    # 파일명이 포함되어 있거나, 일부가 매칭되면 삭제 대상
                    if doc_filename == filename or filename in doc_filename or doc_filename in filename:
                        ids_to_delete.append(all_docs["ids"][i])
                
                if ids_to_delete:
                    self.collection.delete(ids=ids_to_delete)
                    print(f"[RAG] 문서 삭제 완료 (부분 매칭): {filename}, 삭제된 청크 수={len(ids_to_delete)}")
                    return len(ids_to_delete)
                else:
                    print(f"[RAG] 삭제할 문서를 찾을 수 없음: filename={filename}")
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


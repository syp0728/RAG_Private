import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama
from config import *
from .document_processor import DocumentProcessor

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
        self.system_prompt = """너는 기업 내부 문서를 기반으로 답변하는 AI 어시스턴트입니다.

**절대적으로 지켜야 할 규칙:**

1. **컨텍스트 기반 답변만 허용**
   - 반드시 제공된 컨텍스트(Context) 정보만을 사용하여 답변하세요.
   - 컨텍스트에 없는 내용은 절대 추측하거나 지어내지 마세요.

2. **모르는 내용은 솔직하게 답변**
   - 질문에 대한 답변이 컨텍스트에 없으면 반드시 "지식 베이스에 없는 내용입니다"라고 정확히 답변하세요.
   - "~일 수도 있습니다", "~것으로 추정됩니다" 같은 모호한 표현은 사용하지 마세요.

3. **소스 명시 필수**
   - 답변할 때 반드시 어떤 문서의 몇 페이지에서 정보를 가져왔는지 명시하세요.
   - 답변 마지막에 [출처: 파일명, 페이지 X] 형식으로 소스를 명시하세요.

4. **할루시네이션 절대 금지**
   - 컨텍스트에 명확히 나온 정보만 답변에 포함하세요.
   - 일반적인 지식이나 상식을 추가하지 마세요.
   - 컨텍스트의 내용을 변형하거나 확장하지 마세요.

5. **표 정보 처리**
   - 표(table) 정보가 있다면 마크다운 형식으로 정확히 표현하세요.
   - 표의 내용을 자의적으로 해석하지 마세요.

답변 형식:
1. 답변 내용을 먼저 제시합니다.
2. 마지막에 [출처: 파일명, 페이지 X] 형식으로 소스를 명시합니다.
3. 답변할 수 없는 경우 "지식 베이스에 없는 내용입니다"라고만 답변합니다."""
    
    def _get_file_id(self, file_path: Path) -> str:
        """파일 ID 생성"""
        return hashlib.md5(str(file_path).encode()).hexdigest()
    
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
        
        # 메타데이터 준비
        ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_id}_chunk_{i}"
            ids.append(chunk_id)
            metadatas.append({
                "file_id": file_id,
                "filename": filename,
                "page": chunk["page"],
                "type": chunk["type"],
                "chunk_index": i
            })
        
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
    
    def query(self, query_text: str) -> Dict:
        """RAG 질의 처리"""
        import time
        total_start = time.time()
        
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
            
            # 유사 문서 검색
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
        
        # 컨텍스트 구성
        contexts = []
        sources = []
        
        for i, doc_id in enumerate(results["ids"][0]):
            doc_text = results["documents"][0][i]
            metadata = results["metadatas"][0][i]
            
            contexts.append(f"[문서: {metadata['filename']}, 페이지: {metadata['page']}]\n{doc_text}")
            sources.append({
                "filename": metadata["filename"],
                "page": metadata["page"],
                "type": metadata.get("type", "text"),
                "text": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
            })
        
        context_text = "\n\n---\n\n".join(contexts)
        
        # LLM 프롬프트 구성
        user_prompt = f"""다음 컨텍스트를 참고하여 질문에 답변하세요.

[컨텍스트]
{context_text}

[질문]
{query_text}

위 컨텍스트에 없는 내용은 절대 답변하지 마세요. 답변 마지막에 [출처: 파일명, 페이지 X] 형식으로 소스를 명시하세요."""
        
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
        """벡터 DB에서 문서 삭제"""
        try:
            existing = self.collection.get(where={"file_id": file_id})
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
        except Exception as e:
            print(f"Error deleting document: {e}")


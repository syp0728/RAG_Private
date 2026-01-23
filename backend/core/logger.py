# -*- coding: utf-8 -*-
"""
RAG 시스템 로거 - Windows 콘솔 호환 (cp949)
터미널에서 문서 처리 및 쿼리 과정을 상세히 표시
"""
import sys
from datetime import datetime


class RAGLogger:
    """RAG 시스템용 컬러 로거 (Windows 호환)"""
    
    # ANSI 색상 코드 (Windows 10+ 지원)
    class Colors:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        
        # 전경색
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"
        
        # 배경색
        BG_RED = "\033[41m"
        BG_GREEN = "\033[42m"
        BG_YELLOW = "\033[43m"
        BG_BLUE = "\033[44m"
    
    def __init__(self):
        self.enable_colors = True
        self._enable_windows_colors()
    
    def _enable_windows_colors(self):
        """Windows에서 ANSI 색상 지원 활성화"""
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                self.enable_colors = False
    
    def _color(self, color_code):
        """색상 코드 반환 (비활성화 시 빈 문자열)"""
        return color_code if self.enable_colors else ""
    
    def _timestamp(self):
        """현재 시간 포맷"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _safe_print(self, message):
        """안전한 출력 (인코딩 오류 방지)"""
        import sys
        try:
            print(message, flush=True)
        except UnicodeEncodeError:
            # 인코딩 오류 시 ASCII로 변환
            safe_msg = message.encode('ascii', 'replace').decode('ascii')
            print(safe_msg, flush=True)
        sys.stdout.flush()
    
    # ==================== 구분선 ====================
    
    def separator(self, char="=", length=70):
        """구분선 출력"""
        self._safe_print(self._color(self.Colors.DIM) + char * length + self._color(self.Colors.RESET))
    
    def section(self, title):
        """섹션 헤더 출력"""
        self.separator()
        self._safe_print(f"{self._color(self.Colors.BOLD)}{self._color(self.Colors.CYAN)}  {title}{self._color(self.Colors.RESET)}")
        self.separator()
    
    # ==================== 상태 로그 ====================
    
    def info(self, tag, message):
        """일반 정보 로그"""
        timestamp = self._timestamp()
        self._safe_print(
            f"{self._color(self.Colors.DIM)}[{timestamp}]{self._color(self.Colors.RESET)} "
            f"{self._color(self.Colors.BLUE)}[{tag}]{self._color(self.Colors.RESET)} {message}"
        )
    
    def success(self, tag, message):
        """성공 로그"""
        timestamp = self._timestamp()
        self._safe_print(
            f"{self._color(self.Colors.DIM)}[{timestamp}]{self._color(self.Colors.RESET)} "
            f"{self._color(self.Colors.GREEN)}[{tag}] {message}{self._color(self.Colors.RESET)}"
        )
    
    def warning(self, tag, message):
        """경고 로그"""
        timestamp = self._timestamp()
        self._safe_print(
            f"{self._color(self.Colors.DIM)}[{timestamp}]{self._color(self.Colors.RESET)} "
            f"{self._color(self.Colors.YELLOW)}[{tag}] {message}{self._color(self.Colors.RESET)}"
        )
    
    def error(self, tag, message):
        """오류 로그"""
        timestamp = self._timestamp()
        self._safe_print(
            f"{self._color(self.Colors.DIM)}[{timestamp}]{self._color(self.Colors.RESET)} "
            f"{self._color(self.Colors.RED)}[{tag}] ERROR: {message}{self._color(self.Colors.RESET)}"
        )
    
    def step(self, step_num, total, description):
        """단계 표시"""
        progress = f"[{step_num}/{total}]"
        self._safe_print(
            f"  {self._color(self.Colors.YELLOW)}{progress}{self._color(self.Colors.RESET)} {description}"
        )
    
    # ==================== 문서 처리 로그 ====================
    
    def document_upload_start(self, filename, file_ext):
        """문서 업로드 시작"""
        self.section(f"DOCUMENT UPLOAD: {filename}")
        self.info("FILE", f"Extension: {file_ext}")
    
    def document_parsing(self, filename):
        """문서 파싱 시작"""
        self.step(1, 4, f"Parsing document: {filename}")
    
    def document_parsing_complete(self, total_chunks, text_count, table_count, ocr_count=0):
        """문서 파싱 완료"""
        details = f"Total: {total_chunks} chunks"
        if text_count > 0:
            details += f", Text: {text_count}"
        if table_count > 0:
            details += f", Tables: {table_count}"
        if ocr_count > 0:
            details += f", OCR: {ocr_count}"
        self.success("PARSE", details)
    
    def document_chunking(self, chunk_size, overlap):
        """청킹 정보"""
        self.info("CHUNK", f"Chunk size: {chunk_size}, Overlap: {overlap}")
    
    def document_embedding_start(self, num_chunks):
        """임베딩 생성 시작"""
        self.step(2, 4, f"Generating embeddings for {num_chunks} chunks...")
    
    def document_embedding_complete(self, num_chunks, time_taken):
        """임베딩 생성 완료"""
        self.success("EMBED", f"{num_chunks} embeddings generated in {time_taken:.2f}s")
    
    def document_metadata(self, parsed_info):
        """메타데이터 파싱 결과"""
        self.step(3, 4, "Extracting metadata from filename...")
        if parsed_info.get("parsed"):
            self.info("META", f"Date: {parsed_info.get('date', 'N/A')}")
            self.info("META", f"Type: {parsed_info.get('doc_type', 'N/A')}")
            self.info("META", f"Title: {parsed_info.get('doc_title', 'N/A')}")
        else:
            self.warning("META", "Could not parse filename metadata")
    
    def document_save_start(self, num_chunks):
        """벡터 DB 저장 시작"""
        self.step(4, 4, f"Saving {num_chunks} chunks to Vector DB...")
    
    def document_save_complete(self, num_chunks, filename):
        """문서 저장 완료"""
        self.separator("-")
        self.success("COMPLETE", f"Document indexed: {filename}")
        self.success("COMPLETE", f"Total chunks stored: {num_chunks}")
        self.separator()
    
    # ==================== 쿼리 처리 로그 ====================
    
    def query_start(self, query_text):
        """쿼리 처리 시작"""
        display_query = query_text[:60] + "..." if len(query_text) > 60 else query_text
        self.section(f"QUERY: {display_query}")
    
    def query_intent(self, intent_info):
        """쿼리 의도 분석 결과"""
        self.info("INTENT", "Query analysis:")
        if intent_info.get("date"):
            self._safe_print(f"         - Date detected: {intent_info['date']}")
        if intent_info.get("doc_type"):
            self._safe_print(f"         - Document type: {intent_info['doc_type']}")
        if intent_info.get("filename"):
            self._safe_print(f"         - Filename: {intent_info['filename']}")
        if intent_info.get("is_count_query"):
            self._safe_print(f"         - Count query: Yes")
        if intent_info.get("is_full_doc_query"):
            self._safe_print(f"         - Full document query: Yes")
    
    def query_embedding(self, time_taken):
        """쿼리 임베딩 완료"""
        self.step(1, 3, f"Query embedded in {time_taken:.2f}s")
    
    def query_search_start(self, n_results, where_filter=None):
        """벡터 검색 시작"""
        filter_info = f" with filter: {where_filter}" if where_filter else ""
        self.step(2, 3, f"Searching top {n_results} results{filter_info}")
    
    def query_search_complete(self, num_results, filenames, time_taken):
        """벡터 검색 완료"""
        self.success("SEARCH", f"Found {num_results} results in {time_taken:.2f}s")
        unique_files = list(set(filenames))
        if len(unique_files) <= 5:
            self.info("SEARCH", f"Files: {', '.join(unique_files)}")
        else:
            self.info("SEARCH", f"Files: {', '.join(unique_files[:5])}... (+{len(unique_files)-5} more)")
    
    def query_context_build(self, num_chunks, total_chars):
        """컨텍스트 구성"""
        self.info("CONTEXT", f"Building context: {num_chunks} chunks, {total_chars} characters")
    
    def query_llm_start(self, model_name):
        """LLM 호출 시작"""
        self.step(3, 3, f"Generating answer with {model_name}...")
    
    def query_llm_complete(self, time_taken, answer_length):
        """LLM 응답 완료"""
        if time_taken > 10:
            self.warning("LLM", f"Response time: {time_taken:.2f}s (slow!)")
        elif time_taken > 5:
            self.warning("LLM", f"Response time: {time_taken:.2f}s (moderate)")
        else:
            self.success("LLM", f"Response time: {time_taken:.2f}s")
        self.info("LLM", f"Answer length: {answer_length} characters")
    
    def query_complete(self, total_time, sources):
        """쿼리 처리 완료"""
        self.separator("-")
        self.success("COMPLETE", f"Query processed in {total_time:.2f}s")
        if sources:
            source_files = list(set(s.get("filename", "Unknown") for s in sources))
            self.info("SOURCES", f"Referenced: {', '.join(source_files[:3])}")
        self.separator()
    
    # ==================== 시스템 상태 로그 ====================
    
    def system_init(self, component, message):
        """시스템 초기화 로그"""
        self._safe_print(
            f"{self._color(self.Colors.CYAN)}[INIT]{self._color(self.Colors.RESET)} "
            f"{component}: {message}"
        )
    
    def system_ready(self, port):
        """시스템 준비 완료"""
        self.separator("=")
        self._safe_print(
            f"{self._color(self.Colors.GREEN)}{self._color(self.Colors.BOLD)}"
            f"  RAG System Ready - http://localhost:{port}"
            f"{self._color(self.Colors.RESET)}"
        )
        self.separator("=")


# 전역 로거 인스턴스
logger = RAGLogger()


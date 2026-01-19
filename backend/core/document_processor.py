import re
from pathlib import Path
from typing import List, Dict
import PyPDF2
from docx import Document

# unstructured는 선택사항 (설치 실패 시 PyPDF2 사용)
try:
    from unstructured.partition.auto import partition
    from unstructured.chunking.title import chunk_by_title
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False
    print("Warning: unstructured not available, using PyPDF2 fallback")

class DocumentProcessor:
    """Layout-aware 문서 처리 클래스"""
    
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def extract_text_with_layout(self, file_path: Path) -> List[Dict]:
        """
        문서에서 텍스트, 표, 이미지를 추출하여 구조화된 청크 리스트 반환
        각 청크는 페이지 번호와 메타데이터를 포함
        """
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".pdf":
            return self._process_pdf(file_path)
        elif file_ext == ".docx":
            return self._process_docx(file_path)
        elif file_ext in [".txt", ".md"]:
            return self._process_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _process_pdf(self, file_path: Path) -> List[Dict]:
        """PDF 처리 (표 인식 포함)"""
        chunks = []
        
        if HAS_UNSTRUCTURED:
            try:
                # Unstructured를 사용한 구조화된 추출
                elements = partition(filename=str(file_path), strategy="hi_res")
                
                page_num = 1
                current_text = ""
                current_elements = []
                
                for element in elements:
                    element_text = str(element)
                    
                    # 페이지 번호 감지
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'page_number'):
                        new_page = element.metadata.page_number
                        if new_page != page_num:
                            # 페이지 변경 시 현재 청크 저장
                            if current_text.strip():
                                chunks.append({
                                    "text": current_text.strip(),
                                    "page": page_num,
                                    "type": "text"
                                })
                            current_text = ""
                            page_num = new_page
                    
                    # 표(table) 처리
                    if element.category == "Table":
                        # 표를 마크다운 형식으로 변환
                        table_md = self._table_to_markdown(element_text)
                        chunks.append({
                            "text": f"\n\n[표]\n{table_md}\n\n",
                            "page": page_num,
                            "type": "table"
                        })
                    else:
                        current_text += element_text + "\n\n"
                
                # 마지막 청크 저장
                if current_text.strip():
                    chunks.append({
                        "text": current_text.strip(),
                        "page": page_num,
                        "type": "text"
                    })
            
            except Exception as e:
                # Fallback: PyPDF2 사용
                print(f"Unstructured processing failed, using PyPDF2 fallback: {e}")
                self._process_pdf_with_pypdf2(file_path, chunks)
        else:
            # Unstructured가 없으면 PyPDF2 사용
            self._process_pdf_with_pypdf2(file_path, chunks)
        
        # 청크 분할
        return self._chunk_documents(chunks)
    
    def _process_pdf_with_pypdf2(self, file_path: Path, chunks: List[Dict]):
        """PyPDF2를 사용한 PDF 처리 (Fallback)"""
        with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        chunks.append({
                            "text": text.strip(),
                            "page": page_num,
                            "type": "text"
                        })
        
        # 청크 분할
        return self._chunk_documents(chunks)
    
    def _process_docx(self, file_path: Path) -> List[Dict]:
        """DOCX 처리"""
        chunks = []
        doc = Document(file_path)
        
        current_text = ""
        page_num = 1  # DOCX는 정확한 페이지 번호가 없으므로 1로 설정
        
        for para in doc.paragraphs:
            current_text += para.text + "\n\n"
        
        # 표 처리
        for table in doc.tables:
            table_md = self._docx_table_to_markdown(table)
            if current_text.strip():
                chunks.append({
                    "text": current_text.strip(),
                    "page": page_num,
                    "type": "text"
                })
                current_text = ""
            
            chunks.append({
                "text": f"\n\n[표]\n{table_md}\n\n",
                "page": page_num,
                "type": "table"
            })
        
        if current_text.strip():
            chunks.append({
                "text": current_text.strip(),
                "page": page_num,
                "type": "text"
            })
        
        return self._chunk_documents(chunks)
    
    def _process_text(self, file_path: Path) -> List[Dict]:
        """텍스트 파일 처리"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        return self._chunk_documents([{
            "text": text,
            "page": 1,
            "type": "text"
        }])
    
    def _table_to_markdown(self, table_text: str) -> str:
        """표를 마크다운 형식으로 변환"""
        lines = table_text.strip().split("\n")
        if not lines:
            return ""
        
        # 간단한 마크다운 변환
        md_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                md_lines.append("| " + " | ".join(line.split()) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(line.split())) + " |")
            else:
                md_lines.append("| " + " | ".join(line.split()) + " |")
        
        return "\n".join(md_lines)
    
    def _docx_table_to_markdown(self, table) -> str:
        """DOCX 표를 마크다운으로 변환"""
        md_rows = []
        
        for i, row in enumerate(table.rows):
            cells = [cell.text.strip() for cell in row.cells]
            md_rows.append("| " + " | ".join(cells) + " |")
            
            if i == 0:
                md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
        
        return "\n".join(md_rows)
    
    def _chunk_documents(self, chunks: List[Dict]) -> List[Dict]:
        """문서를 지정된 크기로 청크 분할"""
        final_chunks = []
        
        for chunk in chunks:
            text = chunk["text"]
            page = chunk["page"]
            chunk_type = chunk["type"]
            
            if len(text) <= self.chunk_size:
                final_chunks.append({
                    "text": text,
                    "page": page,
                    "type": chunk_type,
                    "metadata": {"page": page, "type": chunk_type}
                })
            else:
                # 텍스트를 더 작은 청크로 분할
                words = text.split()
                current_chunk = []
                current_length = 0
                
                for word in words:
                    word_length = len(word) + 1
                    if current_length + word_length > self.chunk_size and current_chunk:
                        chunk_text = " ".join(current_chunk)
                        final_chunks.append({
                            "text": chunk_text,
                            "page": page,
                            "type": chunk_type,
                            "metadata": {"page": page, "type": chunk_type}
                        })
                        # Overlap을 위해 마지막 부분 유지
                        overlap_size = int(self.chunk_overlap / 10)
                        current_chunk = current_chunk[-overlap_size:] + [word]
                        current_length = sum(len(w) + 1 for w in current_chunk)
                    else:
                        current_chunk.append(word)
                        current_length += word_length
                
                # 마지막 청크
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    final_chunks.append({
                        "text": chunk_text,
                        "page": page,
                        "type": chunk_type,
                        "metadata": {"page": page, "type": chunk_type}
                    })
        
        return final_chunks


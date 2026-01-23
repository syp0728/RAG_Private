"""기존 문서를 pdfplumber로 재인덱싱하는 스크립트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag_system import RAGSystem
from core.file_manager import FileManager
from config import UPLOAD_DIR

def reindex_all_documents():
    """모든 업로드된 문서를 재인덱싱"""
    print("=" * 60)
    print("문서 재인덱싱 시작")
    print("=" * 60)
    
    rag_system = RAGSystem()
    file_manager = FileManager()
    
    # 업로드된 파일 목록 가져오기
    files = file_manager.list_files()
    
    if not files:
        print("재인덱싱할 파일이 없습니다.")
        return
    
    print(f"총 {len(files)}개 파일 발견\n")
    
    success_count = 0
    error_count = 0
    
    for i, file_info in enumerate(files, 1):
        file_id = file_info.get("id")
        filename = file_info.get("filename")
        file_path = Path(UPLOAD_DIR) / f"{file_id}_{filename.replace(' ', '_')}"
        
        # 파일 경로 찾기 (여러 형식 시도)
        if not file_path.exists():
            # 원본 파일명으로 시도
            for f in Path(UPLOAD_DIR).iterdir():
                if f.name.startswith(file_id):
                    file_path = f
                    break
        
        if not file_path.exists():
            print(f"[{i}/{len(files)}] ❌ 파일 없음: {filename}")
            error_count += 1
            continue
        
        print(f"[{i}/{len(files)}] 처리 중: {filename}")
        
        try:
            # 기존 청크 삭제
            existing = rag_system.collection.get(where={"filename": filename})
            if existing["ids"]:
                rag_system.collection.delete(ids=existing["ids"])
                print(f"    - 기존 {len(existing['ids'])}개 청크 삭제")
            
            # 새로 인덱싱
            result = rag_system.index_document(file_path, filename)
            
            # 결과 확인
            new_chunks = rag_system.collection.get(where={"filename": filename})
            table_count = sum(1 for m in new_chunks["metadatas"] if m.get("type") == "table")
            text_count = sum(1 for m in new_chunks["metadatas"] if m.get("type") == "text")
            
            print(f"    - 새로 인덱싱: {len(new_chunks['ids'])}개 청크 (텍스트: {text_count}, 표: {table_count})")
            success_count += 1
            
        except Exception as e:
            print(f"    - ❌ 오류: {e}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print(f"재인덱싱 완료: 성공 {success_count}개, 실패 {error_count}개")
    print("=" * 60)

if __name__ == "__main__":
    reindex_all_documents()


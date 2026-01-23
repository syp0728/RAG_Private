"""
벡터 DB와 파일 시스템 간 동기화 확인 및 정리 스크립트
"""
import sys
sys.path.insert(0, '.')

import chromadb
from pathlib import Path
import json

# 경로 설정 (backend 폴더에서 실행 기준)
SCRIPT_DIR = Path(__file__).parent
VECTOR_DB_DIR = SCRIPT_DIR.parent / "data" / "chroma_db"
UPLOAD_DIR = SCRIPT_DIR.parent / "data" / "uploads"
METADATA_FILE = UPLOAD_DIR / ".file_metadata.json"

def load_file_metadata():
    """파일 메타데이터 로드"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_uploaded_filenames():
    """현재 업로드된 파일 목록"""
    metadata = load_file_metadata()
    filenames = set()
    for file_id, info in metadata.items():
        filenames.add(info.get("original_filename", ""))
    return filenames

def check_sync():
    """동기화 상태 확인"""
    print("=" * 60)
    print("벡터 DB와 파일 시스템 동기화 확인")
    print("=" * 60)
    
    # 1. 파일 시스템의 파일 목록
    uploaded_filenames = get_uploaded_filenames()
    print(f"\n[파일 시스템] 등록된 파일: {len(uploaded_filenames)}개")
    for fn in sorted(uploaded_filenames):
        print(f"  - {fn}")
    
    # 2. 벡터 DB의 파일 목록
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    collection = client.get_collection("enterprise_documents")
    
    all_docs = collection.get()
    vector_filenames = set()
    filename_chunks = {}  # {filename: chunk_count}
    
    for metadata in all_docs["metadatas"]:
        fn = metadata.get("filename", "(없음)")
        vector_filenames.add(fn)
        filename_chunks[fn] = filename_chunks.get(fn, 0) + 1
    
    print(f"\n[벡터 DB] 저장된 파일: {len(vector_filenames)}개, 총 청크: {len(all_docs['ids'])}개")
    for fn in sorted(filename_chunks.keys()):
        status = "OK" if fn in uploaded_filenames else "ORPHAN"
        print(f"  [{status}] {fn}: {filename_chunks[fn]}개 청크")
    
    # 3. 불일치 항목 찾기
    orphan_files = vector_filenames - uploaded_filenames
    missing_files = uploaded_filenames - vector_filenames
    
    print(f"\n[동기화 상태]")
    if orphan_files:
        print(f"  - 고아 데이터 (벡터 DB에만 있음): {len(orphan_files)}개")
        for fn in orphan_files:
            print(f"    * {fn}")
    else:
        print("  - 고아 데이터: 없음")
    
    if missing_files:
        print(f"  - 누락 데이터 (파일만 있음): {len(missing_files)}개")
        for fn in missing_files:
            print(f"    * {fn}")
    else:
        print("  - 누락 데이터: 없음")
    
    return orphan_files, filename_chunks

def cleanup_orphans():
    """고아 데이터 정리"""
    orphan_files, filename_chunks = check_sync()
    
    if not orphan_files:
        print("\n정리할 고아 데이터가 없습니다.")
        return
    
    print(f"\n고아 데이터 {len(orphan_files)}개를 삭제하시겠습니까?")
    response = input("삭제하려면 'yes' 입력: ")
    
    if response.lower() != 'yes':
        print("취소됨")
        return
    
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    collection = client.get_collection("enterprise_documents")
    
    total_deleted = 0
    for fn in orphan_files:
        existing = collection.get(where={"filename": fn})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
            deleted = len(existing["ids"])
            total_deleted += deleted
            print(f"  삭제: {fn} ({deleted}개 청크)")
    
    print(f"\n총 {total_deleted}개 청크 삭제 완료")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_orphans()
    else:
        check_sync()
        print("\n고아 데이터를 정리하려면: python sync_check.py --cleanup")


# -*- coding: utf-8 -*-
"""
벡터 DB 정리 스크립트
업로드 폴더에 없는 문서의 청크를 벡터 DB에서 삭제
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, UPLOAD_DIR

def cleanup_orphan_chunks():
    print("=" * 60)
    print("  Vector DB Cleanup - Removing Orphan Chunks")
    print("=" * 60)
    
    # ChromaDB 연결
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(CHROMA_COLLECTION_NAME)
    
    # 현재 업로드된 파일 목록
    uploaded_files = set()
    for file_path in Path(UPLOAD_DIR).glob("*"):
        if file_path.is_file() and file_path.name != ".file_metadata.json":
            uploaded_files.add(file_path.name)
    
    print(f"\nUploaded files: {len(uploaded_files)}")
    for f in uploaded_files:
        print(f"  - {f}")
    
    # 벡터 DB의 모든 청크 가져오기
    all_docs = collection.get()
    print(f"\nVector DB chunks: {len(all_docs['ids'])}")
    
    # 파일명별 청크 수 집계
    from collections import defaultdict
    file_chunks = defaultdict(list)
    for i, metadata in enumerate(all_docs['metadatas']):
        filename = metadata.get('filename', 'Unknown')
        file_chunks[filename].append(all_docs['ids'][i])
    
    print(f"\nFiles in Vector DB:")
    for filename, chunk_ids in file_chunks.items():
        print(f"  - {filename}: {len(chunk_ids)} chunks")
    
    # 삭제 대상 찾기 (업로드 폴더에 없는 파일)
    orphan_ids = []
    orphan_files = []
    
    for filename, chunk_ids in file_chunks.items():
        # 파일명이 업로드된 파일 중 하나에 포함되어 있는지 확인
        found = False
        for uploaded_file in uploaded_files:
            if filename in uploaded_file or uploaded_file.endswith(filename):
                found = True
                break
        
        if not found:
            orphan_files.append(filename)
            orphan_ids.extend(chunk_ids)
    
    if orphan_ids:
        print(f"\n[!] Orphan files found: {len(orphan_files)}")
        for f in orphan_files:
            print(f"  - {f}")
        
        # 삭제 확인
        confirm = input(f"\nDelete {len(orphan_ids)} orphan chunks? (y/n): ")
        if confirm.lower() == 'y':
            collection.delete(ids=orphan_ids)
            print(f"\n[OK] Deleted {len(orphan_ids)} chunks")
        else:
            print("\n[!] Cancelled")
    else:
        print("\n[OK] No orphan chunks found")
    
    # 최종 상태
    final_count = collection.count()
    print(f"\nFinal Vector DB chunks: {final_count}")
    print("=" * 60)

if __name__ == "__main__":
    cleanup_orphan_chunks()


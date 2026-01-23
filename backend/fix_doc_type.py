# -*- coding: utf-8 -*-
"""
문서 유형 수정 스크립트: '사양서' → '구매사양서'
ChromaDB의 update() 메서드를 사용하여 메타데이터만 수정
"""
import chromadb
from pathlib import Path

VECTOR_DB_DIR = Path(__file__).parent.parent / "data" / "chroma_db"

client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
collection = client.get_collection("enterprise_documents")

# '사양서'로 잘못 저장된 청크 찾기
wrong_doc_type = "사양서"
correct_doc_type = "구매사양서"

all_docs = collection.get(where={"doc_type": wrong_doc_type})

print(f"수정할 청크 수: {len(all_docs['ids'])}개")

if all_docs['ids']:
    for i, doc_id in enumerate(all_docs['ids']):
        old_metadata = all_docs['metadatas'][i]
        print(f"  - {doc_id[:30]}...: page {old_metadata.get('page', '?')}")
    
    # ChromaDB update()로 메타데이터만 수정 (임베딩 유지)
    new_metadatas = []
    for metadata in all_docs['metadatas']:
        metadata['doc_type'] = correct_doc_type
        new_metadatas.append(metadata)
    
    collection.update(
        ids=all_docs['ids'],
        metadatas=new_metadatas
    )
    
    print(f"\n'{wrong_doc_type}' → '{correct_doc_type}'로 {len(all_docs['ids'])}개 청크 수정 완료!")
else:
    print("수정할 청크가 없습니다.")


"""벡터 DB 내용 확인 스크립트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

# ChromaDB 연결
client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection(CHROMA_COLLECTION_NAME)

# 모든 문서 가져오기
all_docs = collection.get()

print(f"총 문서 수: {len(all_docs['ids'])}")
print("\n=== 파일별 그룹화 ===\n")

# 파일명별로 그룹화
file_groups = {}
for i, metadata in enumerate(all_docs['metadatas']):
    filename = metadata.get('filename', 'Unknown')
    file_id = metadata.get('file_id', 'Unknown')
    
    if filename not in file_groups:
        file_groups[filename] = {
            'file_id': file_id,
            'chunks': []
        }
    
    file_groups[filename]['chunks'].append({
        'page': metadata.get('page', 'N/A'),
        'type': metadata.get('type', 'text')
    })

# 결과 출력
for filename, info in file_groups.items():
    print(f"파일명: {filename}")
    print(f"  File ID: {info['file_id']}")
    print(f"  청크 수: {len(info['chunks'])}")
    print()


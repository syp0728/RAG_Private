"""벡터 DB에서 중복 문서 삭제 스크립트"""
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

# 삭제할 파일명 목록 (한글이 제거된 버전)
files_to_delete = [
    "250211__.pdf",
    "250420__.pdf"
]

print("=== 중복 문서 삭제 시작 ===\n")

total_deleted = 0

for filename in files_to_delete:
    try:
        # 해당 파일명의 모든 문서 가져오기
        results = collection.get(where={"filename": filename})
        
        if results["ids"]:
            deleted_count = len(results["ids"])
            # 문서 삭제
            collection.delete(ids=results["ids"])
            print(f"[OK] Deleted: {filename}")
            print(f"   Deleted chunks: {deleted_count}")
            print(f"   File ID: {results['metadatas'][0].get('file_id', 'N/A')}")
            total_deleted += deleted_count
        else:
            print(f"[WARN] Not found: {filename}")
    except Exception as e:
        print(f"[ERROR] Error ({filename}): {e}")

print(f"\n=== 삭제 완료 ===")
print(f"총 삭제된 청크 수: {total_deleted}")

# 삭제 후 확인
print("\n=== 삭제 후 남은 문서 확인 ===\n")
all_docs = collection.get()
file_groups = {}
for metadata in all_docs['metadatas']:
    filename = metadata.get('filename', 'Unknown')
    if filename not in file_groups:
        file_groups[filename] = 0
    file_groups[filename] += 1

for filename, count in sorted(file_groups.items()):
    print(f"{filename}: {count}개 청크")


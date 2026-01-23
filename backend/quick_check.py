# -*- coding: utf-8 -*-
"""벡터 DB 간단 확인"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))
collection = client.get_collection(CHROMA_COLLECTION_NAME)

# 전체 청크 수
all_docs = collection.get()
print(f"Total chunks: {len(all_docs['ids'])}")

# 파일별 청크 수
from collections import defaultdict
file_chunks = defaultdict(list)
for i, m in enumerate(all_docs['metadatas']):
    filename = m.get('filename', 'Unknown')
    file_chunks[filename].append({
        'page': m.get('page'),
        'type': m.get('type'),
        'text': all_docs['documents'][i][:200]
    })

print("\nFile summary:")
for filename, chunks in sorted(file_chunks.items()):
    table_count = sum(1 for c in chunks if c['type'] == 'table')
    text_count = sum(1 for c in chunks if c['type'] == 'text')
    print(f"  {filename}: {len(chunks)} chunks (text: {text_count}, table: {table_count})")

# 250211 재직증명서 상세
target_file = None
for filename in file_chunks.keys():
    if '250211' in filename and '재직증명서' in filename:
        target_file = filename
        break

if target_file:
    print(f"\n=== {target_file} ===")
    chunks = file_chunks[target_file]
    for i, c in enumerate(sorted(chunks, key=lambda x: x['page'])):
        print(f"[Page {c['page']}] ({c['type']}): {c['text'][:150]}...")


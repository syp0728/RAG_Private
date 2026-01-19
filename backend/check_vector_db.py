"""벡터 DB 내용 확인 스크립트"""
import sys
import json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def format_text(text, max_length=100):
    """텍스트를 지정된 길이로 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

# ChromaDB 연결
client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection(CHROMA_COLLECTION_NAME)

# 모든 문서 가져오기
all_docs = collection.get()

print_section("벡터 DB 전체 통계")
print(f"총 청크 수: {len(all_docs['ids'])}")
print(f"컬렉션 이름: {CHROMA_COLLECTION_NAME}")
print(f"저장 경로: {CHROMA_PERSIST_DIR}")

# 파일명별로 그룹화
file_groups = defaultdict(lambda: {
    'file_id': None,
    'chunks': [],
    'metadata': {}
})

for i, metadata in enumerate(all_docs['metadatas']):
    filename = metadata.get('filename', 'Unknown')
    file_id = metadata.get('file_id', 'Unknown')
    
    if file_groups[filename]['file_id'] is None:
        file_groups[filename]['file_id'] = file_id
        file_groups[filename]['metadata'] = {
            'date': metadata.get('date'),
            'doc_type': metadata.get('doc_type'),
            'doc_title': metadata.get('doc_title')
        }
    
    chunk_info = {
        'chunk_id': all_docs['ids'][i],
        'page': metadata.get('page', 'N/A'),
        'type': metadata.get('type', 'text'),
        'chunk_index': metadata.get('chunk_index', i),
        'text_preview': format_text(all_docs['documents'][i], 100)
    }
    file_groups[filename]['chunks'].append(chunk_info)

# 페이지 순서대로 정렬
for filename in file_groups:
    file_groups[filename]['chunks'].sort(key=lambda x: x['page'] if isinstance(x['page'], (int, float)) else 0)

print_section("파일별 상세 정보")
for filename, info in sorted(file_groups.items()):
    print(f"\n📄 파일명: {filename}")
    print(f"   File ID: {info['file_id']}")
    print(f"   청크 수: {len(info['chunks'])}")
    
    meta = info['metadata']
    if meta['date'] or meta['doc_type'] or meta['doc_title']:
        print(f"   메타데이터:")
        if meta['date']:
            print(f"     - 날짜: {meta['date']}")
        if meta['doc_type']:
            print(f"     - 문서 유형: {meta['doc_type']}")
        if meta['doc_title']:
            print(f"     - 문서 제목: {meta['doc_title']}")
    
    # 페이지별 청크 수
    page_counts = defaultdict(int)
    for chunk in info['chunks']:
        page = chunk['page']
        page_counts[page] += 1
    
    print(f"   페이지별 청크 분포:")
    for page in sorted(page_counts.keys()):
        if isinstance(page, (int, float)):
            print(f"     - 페이지 {int(page)}: {page_counts[page]}개 청크")

print_section("문서 유형별 통계")
doc_type_counts = defaultdict(lambda: {'files': set(), 'chunks': 0})

for filename, info in file_groups.items():
    doc_type = info['metadata'].get('doc_type')
    if doc_type:
        doc_type_counts[doc_type]['files'].add(filename)
        doc_type_counts[doc_type]['chunks'] += len(info['chunks'])

for doc_type, counts in sorted(doc_type_counts.items()):
    print(f"  {doc_type}:")
    print(f"    - 파일 수: {len(counts['files'])}")
    print(f"    - 청크 수: {counts['chunks']}")

# 특정 파일의 상세 내용 보기 옵션
print_section("특정 파일의 청크 내용 보기")
print("특정 파일의 상세 내용을 보려면 파일명을 입력하세요 (Enter로 건너뛰기):")
filename_input = input("파일명: ").strip()

if filename_input and filename_input in file_groups:
    info = file_groups[filename_input]
    print(f"\n📄 {filename_input} - 상세 청크 내용")
    print(f"총 {len(info['chunks'])}개 청크\n")
    
    for i, chunk in enumerate(info['chunks'], 1):
        print(f"[청크 {i}]")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  페이지: {chunk['page']}")
        print(f"  타입: {chunk['type']}")
        print(f"  인덱스: {chunk['chunk_index']}")
        print(f"  내용 미리보기: {chunk['text_preview']}")
        print()

# 샘플 메타데이터 확인
print_section("샘플 메타데이터 구조")
if all_docs['metadatas']:
    sample_metadata = all_docs['metadatas'][0]
    print("첫 번째 청크의 메타데이터:")
    print(json.dumps(sample_metadata, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("확인 완료!")
print("=" * 80)


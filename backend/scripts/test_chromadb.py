"""ChromaDB 설치 테스트 스크립트"""
import sys

try:
    import chromadb
    print("✅ ChromaDB import 성공!")
    
    try:
        client = chromadb.Client()
        print("✅ ChromaDB 클라이언트 생성 성공!")
        
        # 간단한 컬렉션 테스트
        collection = client.create_collection("test_collection")
        print("✅ ChromaDB 컬렉션 생성 성공!")
        
        # 테스트 데이터 추가
        collection.add(
            documents=["테스트 문서입니다."],
            ids=["test1"]
        )
        print("✅ ChromaDB 데이터 추가 성공!")
        
        # 테스트 데이터 조회
        results = collection.get(ids=["test1"])
        print(f"✅ ChromaDB 데이터 조회 성공: {results['documents']}")
        
        # 테스트 컬렉션 삭제
        client.delete_collection("test_collection")
        print("✅ ChromaDB 테스트 완료!")
        
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ ChromaDB 작동 중 오류: {e}")
        print("일부 기능이 제한될 수 있습니다.")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ ChromaDB import 실패: {e}")
    print("ChromaDB가 설치되지 않았습니다.")
    sys.exit(1)


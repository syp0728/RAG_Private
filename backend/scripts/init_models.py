"""
초기 모델 다운로드 스크립트
이 스크립트는 처음 실행 시 필요한 모델들을 로컬에 다운로드합니다.
"""
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 상위 디렉토리(backend)를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_MODEL, EMBEDDING_DEVICE, MODELS_DIR, OLLAMA_MODEL

def download_embedding_model():
    """임베딩 모델 다운로드 (CPU용)"""
    print(f"다운로드 중: {EMBEDDING_MODEL} on {EMBEDDING_DEVICE}...")
    
    try:
        model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE,
            cache_folder=str(MODELS_DIR / "sentence-transformers")
        )
        print(f"✅ 임베딩 모델 다운로드 완료: {EMBEDDING_MODEL}")
        return True
    except Exception as e:
        print(f"❌ 임베딩 모델 다운로드 실패: {e}")
        return False

def check_ollama_model():
    """Ollama 모델 확인 안내"""
    from config import OLLAMA_MODEL
    print("\n⚠️  Ollama 모델 다운로드 안내:")
    print(f"   다음 명령어로 Ollama 모델을 다운로드하세요:")
    print(f"   ollama pull {OLLAMA_MODEL}")
    print(f"\n   Ollama가 실행 중인지 확인하세요:")
    print(f"   ollama serve")

if __name__ == "__main__":
    print("=" * 60)
    print("Private RAG - 모델 초기화 스크립트")
    print("=" * 60)
    
    # 임베딩 모델 다운로드
    success = download_embedding_model()
    
    # Ollama 모델 안내
    check_ollama_model()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 초기화 완료!")
    else:
        print("❌ 일부 모델 다운로드 실패")
    print("=" * 60)


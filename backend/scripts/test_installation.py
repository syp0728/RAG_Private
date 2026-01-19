"""설치 확인 스크립트"""
import sys

print(f"Python 버전: {sys.version}")
print(f"Python 실행 경로: {sys.executable}")
print()

# 패키지 테스트
tests = [
    ("chromadb", "ChromaDB"),
    ("onnxruntime", "onnxruntime"),
    ("sentence_transformers", "sentence-transformers"),
    ("ollama", "ollama"),
    ("flask", "Flask"),
    ("langchain", "LangChain"),
]

all_ok = True
for module_name, display_name in tests:
    try:
        __import__(module_name)
        print(f"✅ {display_name}: OK")
    except ImportError as e:
        print(f"❌ {display_name}: 실패 - {e}")
        all_ok = False
    except Exception as e:
        print(f"⚠️ {display_name}: 경고 - {e}")

print()
if all_ok:
    print("✅ 모든 패키지가 정상적으로 설치되었습니다!")
else:
    print("❌ 일부 패키지에 문제가 있습니다.")


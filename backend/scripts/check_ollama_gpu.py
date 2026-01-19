"""Ollama GPU 사용 확인 스크립트"""
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def check_ollama_gpu():
    """Ollama가 GPU를 사용하는지 확인"""
    print("=" * 60)
    print("Ollama GPU Usage Check")
    print("=" * 60)
    
    # Ollama 서버 확인
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[ERROR] Ollama server is not responding")
            return
    except Exception as e:
        print(f"[ERROR] Cannot connect to Ollama: {e}")
        print("\nPlease make sure Ollama is running:")
        print("  ollama serve")
        return
    
    print("[OK] Ollama server is running\n")
    
    # 모델 정보 확인
    try:
        # 모델 정보를 가져오기 위해 간단한 추론 실행
        import ollama
        client = ollama.Client(host="localhost:11434")
        
        # 매우 짧은 테스트 추론
        print("[1] Testing inference performance...")
        start_time = time.time()
        response = client.chat(
            model="llama3.1:8b-instruct-q4_K_M",
            messages=[{"role": "user", "content": "Hi"}],
            options={"num_predict": 10}
        )
        elapsed_time = time.time() - start_time
        
        print(f"    Response time: {elapsed_time:.2f} seconds")
        
        if elapsed_time < 0.5:
            print("    [VERY FAST] Likely using GPU")
        elif elapsed_time < 2.0:
            print("    [FAST] Likely using GPU")
        elif elapsed_time < 5.0:
            print("    [SLOW] Possibly using CPU or GPU with limited resources")
        else:
            print("    [VERY SLOW] Likely using CPU only")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Note: To confirm GPU usage, check Ollama logs when starting:")
    print("  ollama serve")
    print("Look for 'GPU layers: X' in the output")
    print("=" * 60)

if __name__ == "__main__":
    check_ollama_gpu()


"""GPU 사용 확인 스크립트"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
    
    print("=" * 60)
    print("Ollama GPU 사용 확인")
    print("=" * 60)
    
    # Ollama 연결
    client = ollama.Client(host="localhost:11434")
    
    # 모델 정보 확인
    print("\n[1] 모델 목록:")
    models = client.list()
    for model in models.get('models', []):
        print(f"  - {model['name']}")
    
    # 간단한 추론 테스트 (시간 측정)
    print("\n[2] 추론 성능 테스트:")
    test_prompt = "안녕하세요"
    
    start_time = time.time()
    response = client.chat(
        model="llama3.1:8b-instruct-q4_K_M",
        messages=[{"role": "user", "content": test_prompt}],
        options={"num_predict": 50}
    )
    elapsed_time = time.time() - start_time
    
    print(f"  테스트 프롬프트: '{test_prompt}'")
    print(f"  응답 시간: {elapsed_time:.2f}초")
    print(f"  응답 길이: {len(response['message']['content'])}자")
    
    if elapsed_time < 1.0:
        print("  [OK] Fast response (likely using GPU)")
    elif elapsed_time < 3.0:
        print("  [WARN] Normal response (GPU or fast CPU)")
    else:
        print("  [ERROR] Slow response (likely using CPU)")
    
    # Ollama 정보 확인
    print("\n[3] Ollama 정보:")
    try:
        # 환경 변수 확인
        import os
        if "CUDA_VISIBLE_DEVICES" in os.environ:
            print(f"  CUDA_VISIBLE_DEVICES: {os.environ['CUDA_VISIBLE_DEVICES']}")
        else:
            print("  CUDA_VISIBLE_DEVICES: 설정되지 않음")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("참고: GPU 사용 확인은 Ollama 로그에서 확인할 수 있습니다.")
    print("Ollama 실행 시 'GPU layers' 메시지를 확인하세요.")
    print("=" * 60)
    
except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()


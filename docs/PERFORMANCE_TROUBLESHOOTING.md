# 성능 문제 해결 가이드

## 응답이 느린 경우

### 1. GPU 사용 확인

Ollama가 GPU를 사용하는지 확인:

```powershell
# Ollama 실행 시 로그 확인
ollama serve

# GPU 사용 확인 스크립트 실행
cd backend
python scripts/check_gpu.py
```

**Ollama 로그에서 확인할 사항:**
- `GPU layers: X` 메시지가 있으면 GPU 사용 중
- `CPU only` 또는 GPU 관련 메시지가 없으면 CPU 사용 중

### 2. Ollama GPU 설정

Ollama가 GPU를 사용하도록 설정:

#### Windows
Ollama는 자동으로 GPU를 감지합니다. NVIDIA 드라이버가 최신인지 확인하세요.

#### 확인 방법
```powershell
# NVIDIA GPU 확인
nvidia-smi

# Ollama가 GPU를 사용하는지 확인
ollama run llama3.1:8b-instruct-q4_K_M
# 실행 후 "GPU layers" 메시지 확인
```

### 3. 성능 최적화

#### 모델 크기 조정
현재 모델: `llama3.1:8b-instruct-q4_K_M` (약 4.7GB)

더 빠른 모델로 변경:
```powershell
ollama pull llama3.1:8b-instruct-q4_K_S  # 더 작은 모델
```

그리고 `backend/config.py`에서:
```python
OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_S"
```

#### 임베딩 최적화
임베딩은 CPU에서 실행되므로 시간이 걸릴 수 있습니다.
- 첫 실행 시 모델 로딩 시간 포함
- 이후 실행은 캐시 사용으로 더 빠름

### 4. 응답 시간 분석

백엔드 로그에서 각 단계별 시간 확인:

```
[RAG] 임베딩 생성 완료 (X.XX초)
[RAG] 벡터 검색 완료 (X.XX초)
[RAG] Ollama 응답 받음 (X.XX초)  <- 이 부분이 오래 걸리면 GPU 문제
[RAG] 전체 쿼리 처리 완료 (X.XX초)
```

### 5. 일반적인 응답 시간

- **임베딩 생성**: 0.1~0.5초
- **벡터 검색**: 0.1~0.3초
- **LLM 추론 (GPU)**: 1~3초
- **LLM 추론 (CPU)**: 5~15초

총 예상 시간:
- GPU 사용: **1.5~4초**
- CPU 사용: **6~16초**

### 6. 문제 해결 체크리스트

- [ ] Ollama가 실행 중인가?
- [ ] GPU 드라이버가 최신인가? (`nvidia-smi` 확인)
- [ ] Ollama가 GPU를 사용하는가? (로그 확인)
- [ ] 모델이 다운로드되었는가? (`ollama list`)
- [ ] 다른 프로세스가 GPU를 사용 중인가?

### 7. 빠른 해결 방법

```powershell
# 1. Ollama 재시작
# Ollama 종료 후
ollama serve

# 2. GPU 사용 확인
nvidia-smi

# 3. 성능 테스트
cd backend
python scripts/check_gpu.py
```


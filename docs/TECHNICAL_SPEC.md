# Private RAG System - 기술 명세서

> 온프레미스 기반 기업용 RAG(Retrieval-Augmented Generation) 시스템

---

## 1. 프로젝트 개요 (Overview)

### 1.1 목적
- 기업 내부 문서(PDF, DOCX, Excel)를 안전하게 분석하고 질의응답하는 AI 시스템
- 100% 오프라인 동작으로 민감한 데이터의 외부 유출 방지
- 표(Table) 데이터에 특화된 파싱 및 검색 기능

### 1.2 핵심 가치
| 항목 | 설명 |
|------|------|
| **보안** | 모든 데이터가 로컬에서 처리, 외부 API 호출 없음 |
| **정확성** | 하이브리드 검색 + Re-Ranking으로 검색 품질 향상 |
| **표 특화** | 5가지 표 처리 방법으로 복잡한 표도 정확하게 파싱 |
| **확장성** | 모듈화된 구조로 기능 추가 용이 |

---

## 2. 개발 및 인프라 환경 (Environment)

### 2.1 하드웨어 요구사항
| 구성요소 | 최소 사양 | 권장 사양 |
|---------|----------|----------|
| OS | Windows 10/11 | Windows 11 |
| CPU | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| RAM | 16GB | 32GB |
| GPU | NVIDIA GTX 1060 (6GB VRAM) | NVIDIA RTX 4060+ (8GB+ VRAM) |
| Storage | SSD 50GB 여유 공간 | NVMe SSD 100GB+ |

### 2.2 기술 스택

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│  React 18 + Vite 5 + CSS Modules                                │
│  - FileManager.jsx: 파일 업로드/관리 UI                          │
│  - ChatInterface.jsx: 질의응답 인터페이스                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend                                   │
│  Python 3.11 + Flask 3.0                                        │
│  - app.py: REST API 엔드포인트                                   │
│  - rag_system.py: 핵심 RAG 로직                                  │
│  - document_processor.py: 문서 파싱 모듈                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML Components                            │
│  Ollama (llama3.1:8b-instruct-q4_K_M) - LLM 추론                 │
│  SentenceTransformers (bge-m3) - 문서 임베딩                     │
│  ChromaDB - 벡터 데이터베이스                                    │
│  Cross-Encoder (bge-reranker-base) - Re-Ranking                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 주요 라이브러리 버전
```
# Backend
flask==3.0.0
chromadb==0.4.22
sentence-transformers==2.3.1
ollama==0.1.7
pdfplumber>=0.10.0
easyocr>=1.7.0
opencv-python-headless>=4.8.0
rank_bm25>=0.2.2

# Frontend
react: ^18.2.0
vite: ^5.0.0
axios: ^1.6.0
```

### 2.4 개발 도구
| 도구 | 용도 |
|------|------|
| **Cursor Pro** | AI 기반 코드 에디터 (Claude 모델 활용) |
| **Git/GitHub** | 버전 관리 |
| **Ollama** | 로컬 LLM 서버 |
| **PowerShell** | 스크립트 실행 환경 |

---

## 3. 시스템 아키텍처 (Architecture)

### 3.1 전체 파이프라인

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            문서 업로드 파이프라인                          │
└──────────────────────────────────────────────────────────────────────────┘

  문서 업로드 ──▶ 파일 형식 판별 ──▶ 전처리 ──▶ 청킹 ──▶ 임베딩 ──▶ 저장
       │              │               │          │         │         │
       ▼              ▼               ▼          ▼         ▼         ▼
   PDF/DOCX      확장자 확인      OCR/표 파싱   1000자    bge-m3   ChromaDB
   Excel/이미지                   계층 구조 복원 단위      768차원   (벡터+텍스트
                                                 분할      벡터      +메타데이터)


┌──────────────────────────────────────────────────────────────────────────┐
│                             질의응답 파이프라인                            │
└──────────────────────────────────────────────────────────────────────────┘

  사용자 질문 ──▶ 의도 분류 ──▶ 검색 전략 ──▶ 후처리 ──▶ LLM 생성 ──▶ 응답
       │              │            │            │           │          │
       ▼              ▼            ▼            ▼           ▼          ▼
   "250211        GLOBAL/      하이브리드     중복 제거    llama3.1   출처 포함
   재직증명서"    DETAIL        검색          Re-Ranking   8b         답변
                 분류          (Vector+BM25)
```

### 3.2 핵심 알고리즘

#### A. 열 우선 스캔 (Column-first Scan)
```python
# 병합된 셀 처리를 위한 열 단위 순회
for col_idx in range(max_cols):
    last_value = ""
    for row_idx in range(len(table)):
        if cell_value:
            last_value = cell_value
        else:
            # 빈 셀 → 위쪽 값으로 채움 (Fill-down)
            table[row_idx][col_idx] = last_value
```

**효과**: 병합된 셀의 빈 값을 자동으로 채워 계층 구조 복원

#### B. 계층형 텍스트 생성 (Hierarchical Text Construction)
```python
# 출력 형식: "대분류 > 중분류 > 항목 >> 금액: 1000원"
hierarchy_str = " > ".join(hierarchy_parts)
value_str = ", ".join(value_parts)
output = f"  - {hierarchy_str} >> {value_str}"
```

**효과**: 청크가 분리되어도 LLM이 상위 카테고리를 인식 가능

#### C. 동적 검색 전략 (Query Routing)
```python
def _classify_intent(query_text: str) -> str:
    # GLOBAL: "몇 개야?", "목록 알려줘" → 메타데이터 기반 응답
    # DETAIL: "251111 구매사양서 내용" → 하이브리드 검색 + Re-Ranking
    
    global_patterns = [r"몇\s*(개|건)", r"목록", r"전체.*파일"]
    detail_patterns = [r"\d{6}", r"(내용|정보|기준)"]
```

**효과**: 질문 유형에 따라 최적의 검색 전략 자동 선택

---

## 4. 주요 기능 및 코드 설명 (Functionality)

### 4.1 문서 처리 모듈 (`document_processor.py`)

#### 표 처리 5가지 방법
| 방법 | 기술 | 적용 대상 | 메서드 |
|------|------|----------|--------|
| 1 | pdfplumber | 텍스트 기반 PDF 표 | `page.extract_tables()` |
| 2 | EasyOCR | 이미지/스캔 문서 | `reader.readtext()` |
| 3 | OpenCV | 선이 있는 이미지 표 | `cv2.morphologyEx()` |
| 4 | 좌표 추론 | 선이 없는 표 | bbox 기반 행/열 그룹화 |
| 5 | Column-first | 계층 구조 복원 | Forward Fill + 계층 텍스트 |

#### 처리 우선순위
```
PDF 업로드
    │
    ├─▶ OpenCV 표 선 감지 시도
    │       │
    │       ├─ 성공 → 셀별 OCR → Markdown 변환
    │       │
    │       └─ 실패 ↓
    │
    ├─▶ pdfplumber 텍스트 표 추출
    │       │
    │       └─ Column-first Parsing 적용
    │
    └─▶ 일반 텍스트 추출
```

### 4.2 검색 엔진 (`rag_system.py`)

#### 하이브리드 검색 설정
```python
# config.py
VECTOR_WEIGHT = 0.4      # 의미 기반 검색
BM25_WEIGHT = 0.6        # 키워드 기반 검색 (고유명사에 강함)
TOP_K_RESULTS = 40       # 1차 검색 결과 수
RERANK_TOP_K = 25        # Re-Ranking 후 최종 결과 수
```

#### Re-Ranking 프로세스
```python
# Cross-Encoder로 query-document 쌍 점수 계산
reranker_model = "BAAI/bge-reranker-base"

for chunk in search_results:
    score = cross_encoder.predict([(query, chunk.text)])
    chunk.rerank_score = score

# 점수 기준 재정렬
results.sort(key=lambda x: x.rerank_score, reverse=True)
```

### 4.3 데이터베이스 (ChromaDB)

#### 메타데이터 필드 구성
| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `file_id` | str | 파일 고유 ID (MD5 해시) | `"abc123..."` |
| `filename` | str | 원본 파일명 | `"251111_구매사양서_xxx.pdf"` |
| `page` | int | 페이지 번호 | `1` |
| `type` | str | 청크 유형 | `"text"` 또는 `"table"` |
| `date` | str | 문서 날짜 코드 | `"251111"` |
| `doc_type` | str | 문서 유형 | `"구매사양서"` |
| `doc_title` | str | 문서 제목 | `"제조로봇연구_협력작업"` |
| `has_table` | bool | 표 포함 여부 | `True` |
| `file_extension` | str | 파일 확장자 | `".pdf"` |
| `entities_person` | str | 추출된 인명 | `"홍길동, 김철수"` |
| `entities_org` | str | 추출된 조직명 | `"POSCO"` |

#### 저장 구조
```
data/chroma_db/
├── chroma.sqlite3           # 메타데이터 + 청크 ID
├── {collection_id}/
│   ├── data_level0.bin      # 벡터 데이터 (HNSW 인덱스)
│   ├── header.bin           # 인덱스 헤더
│   ├── length.bin           # 벡터 길이
│   └── link_lists.bin       # HNSW 그래프 링크
```

---

## 5. 운영 및 유지보수 (Operation)

### 5.1 실행 방법

#### 초기 설정 (최초 1회)
```powershell
# 1. Ollama 모델 다운로드
ollama pull llama3.1:8b-instruct-q4_K_M

# 2. Backend 설정
cd backend
python -m venv venv311
.\venv311\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Frontend 설정
cd ../frontend
npm install
```

#### 일상 실행
```powershell
# 터미널 1: Backend (Ollama 자동 시작)
cd backend
.\venv311\Scripts\Activate.ps1
python -u app.py

# 터미널 2: Frontend
cd frontend
npm run dev
```

### 5.2 디버깅 가이드

#### 자주 발생하는 오류 및 해결책

| 오류 | 원인 | 해결책 |
|------|------|--------|
| `capture() takes 1 positional argument` | ChromaDB 텔레메트리 버그 | 무시해도 됨 (기능에 영향 없음) |
| `Ollama 연결 실패` | Ollama 서버 미실행 | `ollama serve` 실행 또는 백엔드 재시작 |
| `cp949 codec can't encode` | Windows 인코딩 문제 | `python -u app.py` 사용 |
| `None metadata value` | 메타데이터 파싱 실패 | 파일명 형식 확인 (YYMMDD_유형_제목) |
| LLM 응답 지연 | GPU 메모리 부족 | 다른 GPU 사용 프로그램 종료 |

#### 체크리스트: LLM 응답 품질 저하 시
1. [ ] 벡터 DB에 해당 문서가 제대로 인덱싱되었는지 확인
   ```powershell
   python check_vector_db.py
   ```
2. [ ] 검색 결과가 질문과 관련 있는지 로그 확인
3. [ ] 시스템 프롬프트가 적절한지 검토
4. [ ] 청크 크기/오버랩 조정 검토 (현재: 1000자/200자)

### 5.3 알려진 이슈 및 한계점

| 이슈 | 상세 | 현재 대응 | 향후 계획 |
|------|------|----------|----------|
| 엑셀 복잡 병합 셀 | 3단계 이상 병합 시 인식 오류 가능 | Fill-down 로직 적용 | 병합 셀 좌표 직접 활용 |
| 이미지 OCR 속도 | 페이지당 5-10초 소요 | OpenCV 선처리로 필요 시만 OCR | GPU 가속 OCR 검토 |
| 대용량 문서 | 100페이지 이상 문서 처리 지연 | 청크 배치 처리 | 비동기 처리 도입 |
| 손글씨 인식 | EasyOCR 손글씨 인식률 낮음 | - | TrOCR 등 전문 모델 검토 |

---

## 6. 향후 고도화 계획 (Roadmap)

### Phase 1: 단기 (1-3개월)
| 항목 | 설명 | 우선순위 |
|------|------|----------|
| Docker 컨테이너화 | 배포 및 환경 일관성 확보 | ⭐⭐⭐ |
| 사용자 인증 | 다중 사용자 지원 | ⭐⭐⭐ |
| 대화 기록 저장 | 이전 대화 참조 기능 | ⭐⭐ |
| 배치 업로드 | 여러 파일 동시 처리 | ⭐⭐ |

### Phase 2: 중기 (3-6개월)
| 항목 | 설명 | 기술 |
|------|------|------|
| **VLM 연동** | 이미지 내 텍스트/도표 직접 이해 | LLaVA, GPT-4V 로컬 버전 |
| **다국어 지원** | 영문/일문 문서 처리 | 다국어 임베딩 모델 |
| **실시간 알림** | 새 문서 인덱싱 완료 알림 | WebSocket |

### Phase 3: 장기 (6개월 이상)
| 항목 | 설명 | 기술 |
|------|------|------|
| **Agentic RAG** | 도구 사용(Tool Use) 기능 | LangGraph, AutoGen |
| **Knowledge Graph** | 문서 간 관계 그래프 구축 | Neo4j + RAG |
| **Fine-tuning** | 도메인 특화 모델 학습 | LoRA/QLoRA |

### Agentic RAG 확장 구상
```
┌─────────────────────────────────────────────────────────────────┐
│                      Agentic RAG 아키텍처                        │
└─────────────────────────────────────────────────────────────────┘

  사용자 질문
       │
       ▼
  ┌─────────────┐
  │  Planner    │ ◀─── "이 질문에 답하려면 어떤 도구가 필요한가?"
  │  Agent      │
  └──────┬──────┘
         │
    ┌────┴────┬────────────┬────────────┐
    ▼         ▼            ▼            ▼
┌───────┐ ┌───────┐  ┌───────────┐ ┌───────────┐
│ RAG   │ │ 계산기 │  │ 웹 검색   │ │ 코드 실행  │
│ Tool  │ │ Tool  │  │ Tool     │ │ Tool      │
└───┬───┘ └───┬───┘  └─────┬────┘ └─────┬─────┘
    │         │            │            │
    └────┬────┴────────────┴────────────┘
         │
         ▼
  ┌─────────────┐
  │  Executor   │ ◀─── 도구 결과 종합
  │  Agent      │
  └──────┬──────┘
         │
         ▼
      최종 응답
```

---

## 7. 프로젝트 구조 (Project Structure)

```
RAG_Private/
├── backend/
│   ├── app.py                    # Flask API 서버
│   ├── config.py                 # 설정값 (검색 파라미터 등)
│   ├── requirements.txt          # Python 의존성
│   ├── core/
│   │   ├── rag_system.py         # 핵심 RAG 로직
│   │   ├── document_processor.py # 문서 파싱 (표 5가지 방법)
│   │   ├── filename_parser.py    # 파일명 메타데이터 추출
│   │   └── logger.py             # 터미널 로깅
│   ├── venv311/                  # Python 가상환경
│   └── scripts/
│       └── init_models.py        # 임베딩 모델 초기화
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # 메인 컴포넌트
│   │   ├── components/
│   │   │   ├── FileManager.jsx   # 파일 관리 UI
│   │   │   ├── ChatInterface.jsx # 채팅 UI
│   │   │   └── *.css             # 스타일
│   │   └── main.jsx              # 엔트리포인트
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── uploads/                  # 업로드된 원본 파일
│   ├── chroma_db/                # 벡터 DB 저장소
│   └── models/                   # 임베딩 모델 캐시
│
├── docs/
│   ├── README.md                 # 상세 문서
│   ├── TECHNICAL_SPEC.md         # 기술 명세서 (이 문서)
│   └── *.md                      # 기타 문서
│
└── README.md                     # 빠른 시작 가이드
```

---

## 8. 라이선스 및 기여 (License & Contribution)

### 라이선스
이 프로젝트는 내부 사용 목적으로 개발되었습니다.

### 기여 방법
1. 이슈 등록: 버그 리포트 또는 기능 제안
2. PR 제출: 코드 개선 또는 문서 업데이트

---

*Last Updated: 2026-01-29*
*Version: 1.0.0*


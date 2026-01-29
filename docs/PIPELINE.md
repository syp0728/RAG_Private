# Private RAG System - 파이프라인 상세

---

## Workflow (핵심 흐름)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Private RAG Workflow                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ① 문서 업로드                    ② 구조 분석                   ③ 지능형 청킹
  ─────────────                   ───────────                  ─────────────
  사내 보안망 통해                 OpenCV + OCR로               분석된 구조 정보
  PDF/DOCX/Excel                  표/텍스트 구조 파악           바탕으로 청크 분할
  업로드                          계층 구조 복원                표는 통째로 보존
       │                               │                            │
       └───────────────────────────────┴────────────────────────────┘
                                       │
                                       ▼
                            ④ 벡터 DB 저장
                            ──────────────
                            텍스트 → 768차원 벡터
                            + 구조 메타데이터
                            (문서유형, 날짜, 엔티티)
                            ChromaDB에 통합 저장
                                       │
                                       ▼
                            ⑤ 질문 → 답변 생성
                            ───────────────
                            메타데이터 필터링
                            + 하이브리드 검색
                            + Re-Ranking
                            → LLM 정확한 답변
```

### 단계별 설명

| 단계 | 핵심 기능 | 기술 |
|------|----------|------|
| **① 문서 업로드** | 사내 보안망을 통해 문서 업로드 | 100% 로컬 처리, 외부 API 없음 |
| **② 구조 분석** | 문서의 표/텍스트 구조, 계층 관계 파악 | OpenCV 표 감지, Column-first 파싱 |
| **③ 지능형 청킹** | 분석된 구조 정보를 바탕으로 의미 단위 분할 | 표 보존, 계층형 텍스트 생성 |
| **④ 벡터 DB 저장** | 텍스트 벡터 + 구조 메타데이터 통합 저장 | bge-m3 임베딩, ChromaDB |
| **⑤ 답변 생성** | 메타데이터 필터링 + 검색으로 정확한 답변 | 하이브리드 검색, Re-Ranking, Ollama LLM |

---

## 사용자 파이프라인

### 1단계: 사용자 문서 업로드

#### 문서 파싱
| 파일 형식 | 처리 방법 |
|----------|----------|
| **PDF** | OpenCV 표 선 감지 → pdfplumber 텍스트/표 추출 → 계층형 마크다운 변환 |
| **DOCX** | python-docx → 표 마크다운 변환 → 텍스트 추출 |
| **Excel** | openpyxl/xlrd → 병합 셀 정보 추출 → Column-first Fill → 계층형 텍스트 |
| **이미지** | EasyOCR → 좌표 기반 표 구조 추론 → 텍스트 추출 |

#### 표 처리 5단계
```
1. OpenCV 표 선 감지 시도
   ↓ (실패 시)
2. pdfplumber 텍스트 표 추출
   ↓ (실패 시)
3. EasyOCR 전체 페이지 OCR
   ↓
4. 좌표 기반 행/열 구조 추론
   ↓
5. Column-first Contextual Parsing (계층 구조 복원)
```

#### 청크 생성
| 청크 유형 | 크기 | 용도 |
|----------|------|------|
| **일반 청크** | 1,000자 | 검색 + 답변 생성 통합 |
| **오버랩** | 200자 | 문맥 연속성 보장 |
| **표 청크** | 최대 3,000자 | 표 단위 보존 (분할 최소화) |

---

### 2단계: 벡터화 및 저장

#### 임베딩 생성
```
텍스트 청크 → bge-m3 모델 → 768차원 벡터
           (CPU 기반, 배치 처리)
```

#### 저장 구조
| 저장소 | 내용 | 위치 |
|--------|------|------|
| **ChromaDB** | 벡터 + 원본 텍스트 + 메타데이터 | `data/chroma_db/` |
| **파일 시스템** | 원본 문서 파일 | `data/uploads/` |
| **메타데이터 JSON** | 파일 정보 (ID, 이름, 크기 등) | `data/uploads/.file_metadata.json` |

#### 메타데이터 필드
```python
{
    "file_id": "abc123...",           # MD5 해시
    "filename": "251111_구매사양서_xxx.pdf",
    "page": 1,
    "type": "table",                  # text 또는 table
    "chunk_index": 0,
    
    # 파일명 파싱 결과
    "date": "251111",                 # YYMMDD 형식
    "doc_type": "구매사양서",
    "doc_title": "제조로봇연구_협력작업",
    "file_extension": ".pdf",
    
    # 표 관련
    "has_table": true,
    "table_continued": false,
    
    # 엔티티 추출 결과
    "entities_person": "홍길동, 김철수",
    "entities_org": "POSCO",
    "entities_date": "24.04.16",
    "entities_money": "1,000,000원",
    "entities_location": "포항",
    "entities_product": "레이더센서",
    "entities_keyword": "TLC, 이동위치"
}
```

---

### 3단계: 질문 처리

#### 3-1. 질문 수신 및 의도 분류
```
사용자 질문
    ↓
┌─────────────────────────────────────┐
│         Intent Classifier           │
│  (규칙 기반 + LLM 폴백)              │
└─────────────────────────────────────┘
    ↓                    ↓
[GLOBAL]              [DETAIL]
"몇 개야?"            "251111 구매사양서 내용"
"파일 목록"           "비산먼지 관리기준"
    ↓                    ↓
메타데이터 기반       하이브리드 검색
즉시 응답             + Re-Ranking
```

#### 3-2. 날짜/문서유형 추출 및 필터링
```python
# 질문에서 패턴 추출
날짜 패턴: r"(\d{6})"           # 예: 251111
문서유형: "구매사양서", "재직증명서", "견적서" 등

# ChromaDB where 필터 생성
where = {"$and": [
    {"date": "251111"},
    {"doc_type": "구매사양서"}
]}
```

#### 3-3. 하이브리드 검색
```
질문 텍스트
    ↓
┌─────────────────┬─────────────────┐
│   벡터 검색     │   BM25 검색     │
│   (의미 기반)   │   (키워드 기반)  │
│   가중치: 0.4   │   가중치: 0.6   │
└────────┬────────┴────────┬────────┘
         │                 │
         └────────┬────────┘
                  ↓
         결과 병합 (TOP_K=40)
                  ↓
         ┌───────────────────┐
         │    Re-Ranking     │
         │  (Cross-Encoder)  │
         │  bge-reranker-base│
         └─────────┬─────────┘
                   ↓
         상위 25개 청크 선택
```

#### 3-4. 컨텍스트 구성
```python
# 중복 제거
1단계: (파일명 + 페이지) 기반 중복 제거
2단계: 텍스트 유사도 90% 이상 → 병합

# 파일별 균등 배분 (Round-Robin)
- 파일당 최대 10개 청크
- 최소 15개 ~ 최대 30개 컨텍스트 청크

# 컨텍스트 문자열 생성
[청크 1]
파일명: 251111_구매사양서_xxx.pdf
페이지: 7
문서유형: 구매사양서
내용:
[계층형 표 데이터]
  - 공사현장 > 비산먼지 > 관리기준 >> 분무 살수장치 설치
...
```

#### 3-5. LLM 답변 생성
```
┌─────────────────────────────────────────────────┐
│                 시스템 프롬프트                   │
├─────────────────────────────────────────────────┤
│ 규칙:                                           │
│ 1. 제공된 컨텍스트만 사용하여 답변               │
│ 2. 동일 정보는 한 번만 요약하여 출력             │
│ 3. 마크다운 사용 금지, 순수 텍스트               │
│ 4. 답변 끝에 [출처: 파일명, 페이지] 표기         │
└─────────────────────────────────────────────────┘
                      +
┌─────────────────────────────────────────────────┐
│                  사용자 프롬프트                  │
├─────────────────────────────────────────────────┤
│ [검색된 문서 컨텍스트]                           │
│ {context_string}                                │
│                                                 │
│ [질문]                                          │
│ {user_question}                                 │
└─────────────────────────────────────────────────┘
                      ↓
              Ollama LLM 호출
              (llama3.1:8b)
                      ↓
              답변 텍스트 생성
```

#### LLM 파라미터
```python
options = {
    "temperature": 0.0,      # 결정적 출력
    "top_p": 0.7,            # 핵심 토큰만 샘플링
    "num_predict": 1500,     # 최대 출력 토큰
    "repeat_penalty": 1.2    # 반복 억제
}
```

---

### 4단계: 답변 반환

```
1. 답변 텍스트 생성
   ↓
2. 출처 자동 추가 (누락 시)
   - 최대 5개 출처
   - [출처: 파일명, 페이지 X, Y, Z] 형식
   ↓
3. 프론트엔드 JSON 응답
   {
     "answer": "답변 텍스트...",
     "sources": [
       {"filename": "xxx.pdf", "page": 7},
       {"filename": "xxx.pdf", "page": 8}
     ],
     "processing_time": 2.5
   }
```

---

## 문서 전처리 과정 (상세)

```
1. 파일 업로드 (프론트엔드)
   ↓
2. 파일 저장 + 메타데이터 기록
   - data/uploads/{filename}
   - .file_metadata.json 업데이트
   ↓
3. 파일 형식별 분기
   ┌────────┬────────┬────────┬────────┐
   │  PDF   │  DOCX  │ Excel  │ 이미지  │
   └───┬────┴───┬────┴───┬────┴───┬────┘
       ↓        ↓        ↓        ↓
4. 문서 파싱 (document_processor.py)
   
   [PDF 처리]
   ├─ OpenCV 표 선 감지 시도 (우선)
   │   ├─ 성공: 셀별 EasyOCR → 표 구조화
   │   └─ 실패: 다음 단계로
   │
   ├─ pdfplumber 텍스트 표 추출
   │   ├─ page.extract_tables()
   │   └─ Column-first Fill + 계층형 변환
   │
   └─ 일반 텍스트 추출
       └─ page.extract_text()
   
   [DOCX 처리]
   ├─ 표: doc.tables → 마크다운 변환
   └─ 텍스트: doc.paragraphs
   
   [Excel 처리]
   ├─ 병합 셀 정보 추출 (merged_cells.ranges)
   ├─ Column-first Forward Fill
   └─ 계층형 텍스트 + 마크다운 생성
   
   [이미지 처리]
   └─ EasyOCR → 텍스트 추출
   ↓
5. 청킹 (_chunk_documents)
   
   [표 청크]
   ├─ 3,000자 이하: 분할 안 함 (표 온전히 보존)
   ├─ 3,000자 초과: 행 단위 분할 (헤더 반복)
   └─ 메타데이터: has_table=True
   
   [텍스트 청크]
   ├─ 1,000자 이하: 분할 안 함
   ├─ 1,000자 초과: 단어 단위 분할
   └─ 오버랩: 200자
   ↓
6. 엔티티 추출 (LLM 기반)
   
   질문: "다음 텍스트에서 엔티티를 추출하세요"
   
   추출 대상:
   - person: 인명
   - org: 조직명
   - date_value: 날짜
   - money: 금액
   - location: 장소
   - product: 제품/프로젝트명
   - keyword: 핵심 키워드
   ↓
7. 임베딩 생성
   
   bge-m3 모델 (CPU)
   ├─ 입력: 청크 텍스트
   ├─ 출력: 768차원 벡터
   └─ 배치 처리 (진행률 표시)
   ↓
8. ChromaDB 저장
   
   collection.add(
       ids=[chunk_id, ...],
       embeddings=[vector, ...],
       documents=[text, ...],
       metadatas=[metadata, ...]
   )
   ↓
9. BM25 인덱스 재구축
   
   모든 문서 텍스트로 BM25 인덱스 갱신
   ↓
10. 완료 응답
    
    {
      "success": true,
      "file_id": "abc123...",
      "chunks_count": 25
    }
```

---

## 검색 파이프라인 (상세)

```
1. 질문 수신
   "251111 구매사양서에 있는 비산먼지 관리기준은?"
   ↓
2. 의도 분류 (Intent Classifier)
   
   [규칙 기반 체크]
   ├─ "몇 개", "목록" → GLOBAL
   ├─ 날짜(6자리), "내용", "기준" → DETAIL
   └─ 불명확 → LLM 분류
   
   결과: DETAIL
   ↓
3. 질문 분석
   
   날짜 추출: "251111"
   문서유형 추출: "구매사양서"
   키워드: ["비산먼지", "관리기준"]
   ↓
4. 검색 필터 구성
   
   where = {
       "$and": [
           {"date": "251111"},
           {"doc_type": "구매사양서"}
       ]
   }
   ↓
5. 하이브리드 검색 실행
   
   [벡터 검색]
   query_embedding = bge_m3.encode(질문)
   vector_results = chromadb.query(
       query_embeddings=[query_embedding],
       n_results=40,
       where=where
   )
   
   [BM25 검색]
   tokenized_query = 질문.split()
   bm25_scores = bm25.get_scores(tokenized_query)
   bm25_results = top_k(bm25_scores, k=40)
   
   [결과 병합]
   combined = vector_results * 0.4 + bm25_results * 0.6
   ↓
6. Re-Ranking
   
   pairs = [(질문, chunk.text) for chunk in combined]
   scores = cross_encoder.predict(pairs)
   reranked = sorted(zip(combined, scores), by=score)[:25]
   ↓
7. 엔티티 매칭 가산점
   
   query_entities = extract_entities(질문)
   for chunk in reranked:
       if chunk.entities 교집합 query_entities:
           chunk.score += 가산점
   ↓
8. 중복 제거
   
   [1단계: 파일명+페이지 기반]
   seen = set()
   for chunk in reranked:
       key = (chunk.filename, chunk.page)
       if key in seen:
           skip
       seen.add(key)
   
   [2단계: 텍스트 유사도 기반]
   for chunk in filtered:
       if jaccard_similarity(chunk, existing) >= 0.9:
           merge_pages()
   ↓
9. 컨텍스트 구성
   
   Round-Robin 방식으로 파일별 균등 배분
   최소 15개, 최대 30개 청크
   ↓
10. LLM 호출
    
    response = ollama.chat(
        model="llama3.1:8b-instruct-q4_K_M",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context + question}
        ],
        options={...}
    )
    ↓
11. 응답 후처리
    
    - 출처 누락 시 자동 추가
    - 마크다운 잔여물 제거
    - 응답 JSON 구성
```

---

## 터미널 로그 예시

### 문서 업로드 시
```
============================================================
[INDEX] 문서 인덱싱 시작: 251111_구매사양서_xxx.pdf
============================================================
[INDEX] 1단계: 문서 파싱 중...
[OpenCV] 페이지 1: OpenCV 표 감지 시도 (우선)
[OpenCV] 표 선 감지 시작 (이미지 크기: 1200x1600)
[OpenCV] 셀 24개 감지됨 -> EasyOCR로 셀 내용 추출 중...
[OpenCV TABLE] 페이지 1: 6행 x 4열
    | 구분 | 분류 | 현상 | 관리기준 |
[OpenCV] 표 추출 성공!

[INDEX] 파싱 결과:
    - 총 청크 수: 25
    - 텍스트 청크: 15개
    - 표 청크: 10개

[INDEX] 감지된 표 상세 정보:
    표 1 (페이지 7): [계층형 표 데이터]...
    표 2 (페이지 8): [계층형 표 데이터]...

[INDEX] 2단계: 임베딩 생성 중... (25개 청크)
Batches: 100%|████████████████████| 1/1 [00:05<00:00]

[INDEX] 3단계: 벡터 DB 저장 중...

[INDEX] 저장 완료!
    - 총 저장된 청크: 25개
    - 표 청크 메타데이터:
        페이지 7: has_table=True, type=table
        페이지 8: has_table=True, type=table
============================================================
```

### 질문 처리 시
```
[Intent] 규칙 기반 분류: DETAIL (패턴: \d{6})
[Query] 날짜 추출: 251111
[Query] 문서유형 추출: 구매사양서
[Search] 하이브리드 검색 실행 (Vector: 0.4, BM25: 0.6)
[Search] 1차 검색 결과: 40개 청크
[Rerank] Cross-Encoder 재정렬 중...
[Rerank] 상위 25개 선택
[Context] 중복 제거 후: 18개 청크
[Context] 파일별 배분: 251111_구매사양서_xxx.pdf (10개)
[LLM] Ollama 호출 중...
[LLM] 응답 생성 완료 (2.3초)
```

---

*Last Updated: 2026-01-29*


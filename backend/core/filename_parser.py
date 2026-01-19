"""파일명 파싱 유틸리티"""
import re
from typing import Dict, Optional

def parse_filename(filename: str) -> Dict[str, Optional[str]]:
    """
    파일명을 파싱하여 메타데이터 추출
    형식: (날짜)_(문서유형)_문서제목.확장자
    
    예시:
    - "250211_재직증명서_센싱플러스.pdf" 
      -> {"date": "250211", "doc_type": "재직증명서", "doc_title": "센싱플러스"}
    - "250420_회의록_프로젝트회의.pdf"
      -> {"date": "250420", "doc_type": "회의록", "doc_title": "프로젝트회의"}
    """
    # 확장자 제거
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # 패턴: (날짜 6자리)_(문서유형)_(문서제목)
    pattern = r'^(\d{6})_(.+?)_(.+)$'
    match = re.match(pattern, name_without_ext)
    
    if match:
        date = match.group(1)
        doc_type = match.group(2)
        doc_title = match.group(3)
        
        return {
            "date": date,
            "doc_type": doc_type,
            "doc_title": doc_title,
            "parsed": True
        }
    else:
        # 패턴이 맞지 않는 경우
        return {
            "date": None,
            "doc_type": None,
            "doc_title": None,
            "parsed": False
        }

def format_date(date_str: str) -> str:
    """
    날짜 문자열을 읽기 쉬운 형식으로 변환
    "250211" -> "2025년 02월 11일"
    """
    if not date_str or len(date_str) != 6:
        return date_str
    
    try:
        year = "20" + date_str[:2]
        month = date_str[2:4]
        day = date_str[4:6]
        return f"{year}년 {month}월 {day}일"
    except:
        return date_str


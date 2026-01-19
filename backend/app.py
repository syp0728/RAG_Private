from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from config import *
from core.rag_system import RAGSystem
from core.file_manager import FileManager

app = Flask(__name__)
CORS(app)

# RAG 시스템 및 파일 매니저 초기화
rag_system = RAGSystem()
file_manager = FileManager()

@app.route("/api/health", methods=["GET"])
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({"status": "healthy", "message": "Private RAG API is running"})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """파일 업로드 및 인덱싱"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        
        # 파일 확장자 검증
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Unsupported file type: {file_ext}"}), 400
        
        # 원본 파일명 저장 (secure_filename 적용 전)
        original_filename = file.filename
        # 파일 저장용 안전한 파일명 생성
        safe_filename = secure_filename(file.filename)
        file_path = file_manager.save_file(file, safe_filename, original_filename)
        
        # 문서 인덱싱 (원본 파일명 사용)
        result = rag_system.index_document(file_path, original_filename)
        
        return jsonify({
            "success": True,
            "filename": original_filename,  # 원본 파일명 반환
            "file_id": result["file_id"],
            "chunks_count": result["chunks_count"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files", methods=["GET"])
def list_files():
    """업로드된 파일 목록 조회"""
    try:
        files = file_manager.list_files()
        
        # 파일명 파싱하여 메타데이터 추가
        from core.filename_parser import parse_filename
        for file in files:
            parsed_info = parse_filename(file["filename"])
            if parsed_info["parsed"]:
                file["date"] = parsed_info["date"]
                file["doc_type"] = parsed_info["doc_type"]
                file["doc_title"] = parsed_info["doc_title"]
            else:
                file["date"] = None
                file["doc_type"] = None
                file["doc_title"] = None
        
        # 필터링 파라미터 처리
        doc_type = request.args.get("doc_type")
        date = request.args.get("date")
        
        if doc_type:
            files = [f for f in files if f.get("doc_type") == doc_type]
        if date:
            files = [f for f in files if f.get("date") == date]
        
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/<file_id>", methods=["GET"])
def download_file(file_id):
    """원본 파일 다운로드"""
    try:
        file_path = file_manager.get_file_path(file_id)
        if not file_path or not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=file_path.name
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/query", methods=["POST"])
def query():
    """RAG 쿼리 처리"""
    try:
        data = request.json
        query_text = data.get("query")
        
        if not query_text:
            return jsonify({"error": "Query text is required"}), 400
        
        print(f"쿼리 수신: {query_text[:50]}...")
        
        # RAG 질의 처리
        result = rag_system.query(query_text)
        
        print(f"쿼리 처리 완료: has_answer={result.get('has_answer')}, sources={len(result.get('sources', []))}")
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
            "has_answer": result["has_answer"]
        }), 200
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"쿼리 처리 오류:")
        print(error_detail)
        return jsonify({
            "error": str(e),
            "answer": f"오류가 발생했습니다: {str(e)}",
            "sources": [],
            "has_answer": False
        }), 500

@app.route("/api/files/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    """파일 및 인덱스 삭제"""
    try:
        # 파일 경로 가져오기
        file_path = file_manager.get_file_path(file_id)
        
        # 벡터 DB에서 문서 삭제 (파일 경로 기반)
        if file_path:
            rag_system.delete_document_by_path(file_path)
        else:
            # 파일 경로를 찾을 수 없으면 file_id로 직접 삭제 시도
            rag_system.delete_document(file_id)
        
        # 파일 삭제
        file_manager.delete_file(file_id)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        import traceback
        print(f"파일 삭제 오류: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"Starting Private RAG API server...")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"Embedding Device: {EMBEDDING_DEVICE}")
    app.run(host="0.0.0.0", port=5000, debug=False)


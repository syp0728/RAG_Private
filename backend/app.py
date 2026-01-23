from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from werkzeug.utils import secure_filename
from config import *

# 출력 버퍼링 비활성화 (로그 실시간 출력)
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None


def check_ollama_running():
    """Ollama 서버가 실행 중인지 확인"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_ollama_server():
    """Ollama 서버를 백그라운드로 시작"""
    print("[OLLAMA] Checking Ollama server status...")
    
    if check_ollama_running():
        print("[OLLAMA] Ollama server is already running")
        return True
    
    print("[OLLAMA] Starting Ollama server...")
    
    try:
        # Windows에서 백그라운드로 ollama serve 실행
        if sys.platform == "win32":
            # DETACHED_PROCESS 플래그로 별도 프로세스로 실행
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            # Linux/Mac
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Ollama가 준비될 때까지 대기 (최대 30초)
        print("[OLLAMA] Waiting for Ollama to be ready...")
        for i in range(30):
            time.sleep(1)
            if check_ollama_running():
                print(f"[OLLAMA] Ollama server started successfully (took {i+1}s)")
                return True
            if (i + 1) % 5 == 0:
                print(f"[OLLAMA] Still waiting... ({i+1}s)")
        
        print("[OLLAMA] WARNING: Ollama server did not start within 30 seconds")
        print("[OLLAMA] Please check if Ollama is installed correctly")
        return False
        
    except FileNotFoundError:
        print("[OLLAMA] ERROR: 'ollama' command not found")
        print("[OLLAMA] Please install Ollama from https://ollama.ai")
        return False
    except Exception as e:
        print(f"[OLLAMA] ERROR: Failed to start Ollama: {e}")
        return False


# Ollama 서버 자동 시작
start_ollama_server()

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
        
        # 중복 문서 확인
        duplicate_check = rag_system.check_duplicate_document(original_filename)
        if duplicate_check["is_duplicate"]:
            return jsonify({
                "error": "Duplicate document",
                "message": duplicate_check["message"],
                "existing_file_id": duplicate_check["existing_file_id"],
                "is_duplicate": True
            }), 409  # 409 Conflict
        
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
        
        # 통계 정보 계산 (필터링 전 전체 데이터 기준)
        # 전체 문서 개수 (고유 파일명 기준)
        total_count = len(files)
        
        # 문서 유형별 개수 계산 (필터링 전)
        doc_type_counts = {}
        for file in files:
            file_doc_type = file.get("doc_type")
            if file_doc_type:
                if file_doc_type not in doc_type_counts:
                    doc_type_counts[file_doc_type] = 0
                doc_type_counts[file_doc_type] += 1
        
        # 벡터 DB에서도 문서 유형별 개수 가져오기 (더 정확한 정보)
        try:
            vector_db_stats = rag_system.get_all_document_types()
            # 벡터 DB의 정보가 더 정확할 수 있으므로 우선 사용
            # 하지만 파일 목록에 없는 문서 유형도 포함될 수 있으므로 병합
            for doc_type, count in vector_db_stats.items():
                if doc_type not in doc_type_counts or count > doc_type_counts[doc_type]:
                    doc_type_counts[doc_type] = count
        except Exception as e:
            print(f"[API] 벡터 DB 통계 조회 오류: {e}")
            # 벡터 DB 조회 실패 시 파일 목록 기반 통계만 사용
        
        # 통계 정보 구성
        statistics = {
            "total_count": total_count,
            "by_doc_type": doc_type_counts
        }
        
        # 필터링 파라미터 처리 (통계 계산 후)
        doc_type = request.args.get("doc_type")
        date = request.args.get("date")
        
        if doc_type:
            files = [f for f in files if f.get("doc_type") == doc_type]
        if date:
            files = [f for f in files if f.get("date") == date]
        
        return jsonify({
            "files": files,
            "statistics": statistics
        }), 200
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
        from core.logger import logger
        logger.info("DELETE", f"Deleting file: file_id={file_id}")
        
        # 파일 정보 가져오기 (원본 파일명 포함)
        file_info = None
        for f in file_manager.list_files():
            if f["id"] == file_id:
                file_info = f
                break
        
        # 벡터 DB에서 문서 삭제 (원본 파일명으로 검색)
        deleted_chunks = 0
        if file_info:
            original_filename = file_info.get("filename")
            logger.info("DELETE", f"Original filename: {original_filename}")
            deleted_chunks = rag_system.delete_document_by_filename(original_filename)
        
        # 파일명으로 삭제 안 되면 file_id와 경로로 시도
        if deleted_chunks == 0:
            file_path = file_manager.get_file_path(file_id)
            if file_path:
                deleted_chunks = rag_system.delete_document_by_path(file_path)
            if deleted_chunks == 0:
                deleted_chunks = rag_system.delete_document(file_id)
        
        logger.success("DELETE", f"Deleted {deleted_chunks} chunks from vector DB")
        
        # 파일 삭제
        file_manager.delete_file(file_id)
        logger.success("DELETE", f"File deleted: file_id={file_id}")
        
        return jsonify({"success": True, "deleted_chunks": deleted_chunks}), 200
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


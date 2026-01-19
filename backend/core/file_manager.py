import hashlib
import uuid
from pathlib import Path
from config import UPLOAD_DIR

class FileManager:
    """파일 업로드 및 다운로드 관리"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.file_registry = {}  # file_id -> file_info 매핑
    
    def _generate_file_id(self, filename):
        """파일 ID 생성 (해시 기반)"""
        return hashlib.md5(filename.encode()).hexdigest()
    
    def save_file(self, file, filename):
        """파일 저장 및 ID 반환"""
        file_id = self._generate_file_id(filename)
        file_path = self.upload_dir / f"{file_id}_{filename}"
        
        file.save(str(file_path))
        
        # 레지스트리에 등록
        self.file_registry[file_id] = {
            "id": file_id,
            "filename": filename,
            "path": file_path,
            "size": file_path.stat().st_size
        }
        
        return file_path
    
    def get_file_path(self, file_id):
        """파일 ID로 파일 경로 조회"""
        if file_id in self.file_registry:
            return self.file_registry[file_id]["path"]
        
        # 레지스트리에 없으면 파일 시스템에서 검색
        for file_path in self.upload_dir.glob(f"{file_id}_*"):
            return file_path
        
        return None
    
    def list_files(self):
        """업로드된 파일 목록 반환"""
        files = []
        for file_path in self.upload_dir.glob("*"):
            if file_path.is_file():
                file_id = file_path.stem.split("_", 1)[0]
                files.append({
                    "id": file_id,
                    "filename": file_path.name.split("_", 1)[1] if "_" in file_path.name else file_path.name,
                    "size": file_path.stat().st_size
                })
        return files
    
    def delete_file(self, file_id):
        """파일 삭제"""
        file_path = self.get_file_path(file_id)
        if file_path and file_path.exists():
            file_path.unlink()
            if file_id in self.file_registry:
                del self.file_registry[file_id]
            return True
        return False


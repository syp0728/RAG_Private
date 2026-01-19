import hashlib
import uuid
import json
from pathlib import Path
from config import UPLOAD_DIR

class FileManager:
    """파일 업로드 및 다운로드 관리"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.file_registry = {}  # file_id -> file_info 매핑
        self.metadata_file = self.upload_dir / ".file_metadata.json"
        self._load_metadata()
    
    def _generate_file_id(self, filename):
        """파일 ID 생성 (해시 기반)"""
        return hashlib.md5(filename.encode()).hexdigest()
    
    def _load_metadata(self):
        """메타데이터 파일에서 원본 파일명 정보 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    for file_id, info in metadata.items():
                        if file_id not in self.file_registry:
                            # 파일 경로 재구성
                            safe_filename = info.get('safe_filename', '')
                            file_path = self.upload_dir / f"{file_id}_{safe_filename}"
                            if file_path.exists():
                                self.file_registry[file_id] = {
                                    "id": file_id,
                                    "filename": info.get('original_filename', safe_filename),
                                    "path": file_path,
                                    "size": file_path.stat().st_size
                                }
            except Exception as e:
                print(f"메타데이터 로드 오류: {e}")
    
    def _save_metadata(self):
        """메타데이터 파일에 원본 파일명 정보 저장"""
        metadata = {}
        for file_id, info in self.file_registry.items():
            if info["path"].exists():
                metadata[file_id] = {
                    "original_filename": info["filename"],
                    "safe_filename": info["path"].name.split("_", 1)[1] if "_" in info["path"].name else info["path"].name
                }
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메타데이터 저장 오류: {e}")
    
    def save_file(self, file, safe_filename, original_filename=None):
        """파일 저장 및 ID 반환"""
        # 원본 파일명이 없으면 safe_filename 사용
        if original_filename is None:
            original_filename = safe_filename
        
        # file_id는 원본 파일명 기반으로 생성 (일관성 유지)
        file_id = self._generate_file_id(original_filename)
        file_path = self.upload_dir / f"{file_id}_{safe_filename}"
        
        file.save(str(file_path))
        
        # 레지스트리에 등록 (원본 파일명 저장)
        self.file_registry[file_id] = {
            "id": file_id,
            "filename": original_filename,  # 원본 파일명 저장
            "path": file_path,
            "size": file_path.stat().st_size
        }
        
        # 메타데이터 저장
        self._save_metadata()
        
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
        
        # 먼저 레지스트리에서 파일 정보 가져오기 (원본 파일명 보존)
        for file_id, file_info in self.file_registry.items():
            if file_info["path"].exists():
                files.append({
                    "id": file_id,
                    "filename": file_info["filename"],  # 원본 파일명 사용
                    "size": file_info["size"]
                })
        
        # 레지스트리에 없는 파일은 파일 시스템에서 검색
        registered_ids = {f["id"] for f in files}
        
        # 메타데이터 파일에서 원본 파일명 정보 로드 시도
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    for file_id, info in metadata.items():
                        if file_id not in registered_ids:
                            # 파일 경로 재구성
                            safe_filename = info.get('safe_filename', '')
                            file_path = self.upload_dir / f"{file_id}_{safe_filename}"
                            if file_path.exists():
                                files.append({
                                    "id": file_id,
                                    "filename": info.get('original_filename', safe_filename),
                                    "size": file_path.stat().st_size
                                })
                                registered_ids.add(file_id)
            except Exception as e:
                print(f"메타데이터 로드 오류: {e}")
        
        # 여전히 레지스트리에 없는 파일은 파일 시스템에서 검색
        for file_path in self.upload_dir.glob("*"):
            if file_path.is_file() and file_path.name != ".file_metadata.json":
                # 파일명 형식: {file_id}_{safe_filename}
                # file_id는 MD5 해시이므로 32자리
                file_name = file_path.name
                
                # 파일명에서 file_id 추출 (32자리 MD5 해시)
                if len(file_name) > 33 and file_name[32] == '_':
                    file_id = file_name[:32]
                    if file_id not in registered_ids:
                        # safe_filename 추출 (file_id_ 이후의 모든 내용)
                        safe_filename = file_name[33:]  # 32자리 file_id + '_' = 33자리
                        files.append({
                            "id": file_id,
                            "filename": safe_filename,  # 메타데이터가 없으면 safe_filename 사용
                            "size": file_path.stat().st_size
                        })
                else:
                    # 형식이 맞지 않는 경우 (레거시 파일)
                    # 파일명에서 첫 번째 _ 이후를 파일명으로 간주
                    if "_" in file_name:
                        parts = file_name.split("_", 1)
                        file_id = parts[0]
                        if file_id not in registered_ids:
                            files.append({
                                "id": file_id,
                                "filename": parts[1] if len(parts) > 1 else file_name,
                                "size": file_path.stat().st_size
                            })
                    else:
                        # 파일명에 _가 없는 경우 (레거시 파일)
                        file_id = file_path.stem
                        if file_id not in registered_ids:
                            files.append({
                                "id": file_id,
                                "filename": file_name,
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
            # 메타데이터 업데이트
            self._save_metadata()
            return True
        return False


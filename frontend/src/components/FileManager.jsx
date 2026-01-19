import React, { useState, useRef } from 'react'
import './FileManager.css'

function FileManager({ files, onUpload, onDelete, onDownload, backendStatus }) {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setUploadStatus(null)

    const result = await onUpload(file)

    setUploading(false)
    setUploadStatus(result)

    // 파일 입력 초기화
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }

    // 3초 후 상태 메시지 제거
    if (result.success) {
      setTimeout(() => setUploadStatus(null), 3000)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return (
    <div className="file-manager">
      <div className="file-manager-header">
        <h2>파일 관리</h2>
        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            id="file-upload"
            className="file-input"
            onChange={handleFileSelect}
            accept=".pdf,.docx,.txt,.md"
            disabled={uploading || backendStatus === 'offline'}
          />
          <label
            htmlFor="file-upload"
            className={`upload-button ${uploading ? 'uploading' : ''} ${backendStatus === 'offline' ? 'disabled' : ''}`}
            title={backendStatus === 'offline' ? '백엔드 서버에 연결할 수 없습니다' : ''}
          >
            {uploading ? '업로드 중...' : backendStatus === 'offline' ? '⚠️ 연결 필요' : '📁 파일 업로드'}
          </label>
          {uploadStatus && (
            <div className={`upload-status ${uploadStatus.success ? 'success' : 'error'}`}>
              {uploadStatus.success
                ? '✅ 업로드 및 인덱싱 완료'
                : `❌ ${uploadStatus.error || '업로드 실패'}`}
            </div>
          )}
        </div>
      </div>

      <div className="file-list">
        {files.length === 0 ? (
          <div className="file-empty">
            <p>📄 업로드된 파일이 없습니다.</p>
            <p className="file-hint">
              PDF, DOCX, TXT, MD 형식의 파일을 업로드할 수 있습니다.
            </p>
          </div>
        ) : (
          <table className="file-table">
            <thead>
              <tr>
                <th>파일명</th>
                <th>크기</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr key={file.id}>
                  <td className="file-name">{file.filename}</td>
                  <td className="file-size">{formatFileSize(file.size)}</td>
                  <td className="file-actions">
                    <button
                      className="action-button download"
                      onClick={() => onDownload(file.id)}
                      title="다운로드"
                    >
                      📥
                    </button>
                    <button
                      className="action-button delete"
                      onClick={() => {
                        if (window.confirm(`"${file.filename}"을(를) 삭제하시겠습니까?`)) {
                          onDelete(file.id)
                        }
                      }}
                      title="삭제"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default FileManager


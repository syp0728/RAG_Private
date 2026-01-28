import React, { useState, useRef } from 'react'
import './FileManager.css'

function FileManager({ files, statistics, onUpload, onDelete, onDownload, backendStatus }) {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [filterDocType, setFilterDocType] = useState('')
  const [filterDate, setFilterDate] = useState('')
  const fileInputRef = useRef(null)
  
  // 문서 유형 목록 추출 (통계 정보 사용)
  const docTypes = Object.keys(statistics.by_doc_type || {}).sort()
  
  // 날짜 목록 추출
  const dates = [...new Set(files.map(f => f.date).filter(Boolean))].sort().reverse()
  
  // 필터링된 파일 목록
  const filteredFiles = files.filter(file => {
    if (filterDocType && file.doc_type !== filterDocType) return false
    if (filterDate && file.date !== filterDate) return false
    return true
  })

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

  const getFileExtension = (filename) => {
    if (!filename) return '-'
    const ext = filename.split('.').pop()?.toUpperCase()
    return ext || '-'
  }

  const getExtensionClass = (filename) => {
    const ext = filename?.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf': return 'ext-pdf'
      case 'docx': case 'doc': return 'ext-docx'
      case 'xlsx': case 'xls': return 'ext-xlsx'
      case 'txt': case 'md': return 'ext-txt'
      case 'png': case 'jpg': case 'jpeg': case 'gif': return 'ext-img'
      default: return 'ext-other'
    }
  }

  return (
    <div className="file-manager">
      <div className="file-manager-header">
        <div className="file-manager-title-section">
          <h2>파일 관리</h2>
          <div className="file-statistics">
            <span className="stat-total">전체 문서: {statistics.total_count || files.length}개</span>
          </div>
        </div>
        <div className="file-filters">
          <select
            className="filter-select"
            value={filterDocType}
            onChange={(e) => setFilterDocType(e.target.value)}
          >
            <option value="">전체 문서 유형</option>
            {docTypes.map(type => (
              <option key={type} value={type}>
                {type}({statistics.by_doc_type[type] || 0})
              </option>
            ))}
          </select>
          <select
            className="filter-select"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
          >
            <option value="">전체 날짜</option>
            {dates.map(date => (
              <option key={date} value={date}>
                {date ? `${date.substring(0, 2)}년 ${date.substring(2, 4)}월 ${date.substring(4, 6)}일` : date}
              </option>
            ))}
          </select>
          {(filterDocType || filterDate) && (
            <button
              className="filter-clear"
              onClick={() => {
                setFilterDocType('')
                setFilterDate('')
              }}
            >
              필터 초기화
            </button>
          )}
        </div>
        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            id="file-upload"
            className="file-input"
            onChange={handleFileSelect}
            accept=".pdf,.docx,.txt,.md,.xlsx,.xls,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.tif,.webp"
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
        {filteredFiles.length === 0 ? (
          <div className="file-empty">
            <p>📄 {files.length === 0 ? '업로드된 파일이 없습니다.' : '필터 조건에 맞는 파일이 없습니다.'}</p>
            <p className="file-hint">
              {files.length === 0 
                ? 'PDF, DOCX, TXT, MD, XLSX, XLS 형식의 파일을 업로드할 수 있습니다.'
                : '다른 필터 조건을 선택해보세요.'}
            </p>
          </div>
        ) : (
          <table className="file-table">
            <thead>
              <tr>
                <th>날짜</th>
                <th>문서 유형</th>
                <th>문서 제목</th>
                <th>확장자</th>
                <th>크기</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {filteredFiles.map((file) => (
                <tr key={file.id}>
                  <td className="file-date">
                    {file.date 
                      ? `${file.date.substring(0, 2)}년 ${file.date.substring(2, 4)}월 ${file.date.substring(4, 6)}일`
                      : '-'}
                  </td>
                  <td className="file-doc-type">{file.doc_type || '-'}</td>
                  <td className="file-title">
                    {file.doc_title || file.filename}
                    {!file.doc_type && (
                      <span className="file-filename-hint" title={file.filename}>
                        ({file.filename})
                      </span>
                    )}
                  </td>
                  <td className="file-extension">
                    <span className={`extension-badge ${getExtensionClass(file.filename)}`}>
                      {getFileExtension(file.filename)}
                    </span>
                  </td>
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


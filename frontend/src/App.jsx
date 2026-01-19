import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import FileManager from './components/FileManager'
import api from './services/api'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [files, setFiles] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking') // 'online', 'offline', 'checking'

  // 백엔드 연결 상태 확인
  const checkBackendStatus = async () => {
    try {
      const response = await api.get('/health')
      if (response.data.status === 'healthy') {
        setBackendStatus('online')
      } else {
        setBackendStatus('offline')
      }
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  useEffect(() => {
    // 초기 상태 확인
    checkBackendStatus()
    loadFiles()

    // 주기적으로 상태 확인 (5초마다)
    const statusInterval = setInterval(checkBackendStatus, 5000)

    return () => {
      clearInterval(statusInterval)
    }
  }, [])

  const loadFiles = async () => {
    try {
      const response = await api.get('/files')
      setFiles(response.data.files || [])
    } catch (error) {
      console.error('파일 목록 로드 실패:', error)
    }
  }

  const handleFileUpload = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      await loadFiles()
      return { success: true }
    } catch (error) {
      console.error('파일 업로드 실패:', error)
      return { success: false, error: error.response?.data?.error || '업로드 실패' }
    }
  }

  const handleFileDelete = async (fileId) => {
    try {
      await api.delete(`/files/${fileId}`)
      await loadFiles()
      return { success: true }
    } catch (error) {
      console.error('파일 삭제 실패:', error)
      return { success: false, error: error.response?.data?.error || '삭제 실패' }
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🔒 Private RAG AI Agent</h1>
            <p>온프레미스 기반 기업용 RAG 시스템</p>
          </div>
          <div className="backend-status">
            <div className={`status-indicator ${backendStatus}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                {backendStatus === 'online' && '백엔드 연결됨'}
                {backendStatus === 'offline' && '백엔드 연결 끊김'}
                {backendStatus === 'checking' && '연결 확인 중...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          💬 채팅
        </button>
        <button
          className={activeTab === 'files' ? 'active' : ''}
          onClick={() => setActiveTab('files')}
        >
          📁 파일 관리
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'chat' && (
          <ChatInterface backendStatus={backendStatus} />
        )}
        {activeTab === 'files' && (
          <FileManager
            files={files}
            onUpload={handleFileUpload}
            onDelete={handleFileDelete}
            onDownload={(fileId) => {
              window.open(`/api/files/${fileId}`, '_blank')
            }}
            backendStatus={backendStatus}
          />
        )}
      </main>
    </div>
  )
}

export default App


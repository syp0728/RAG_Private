import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import ChatSidebar from './components/ChatSidebar'
import FileManager from './components/FileManager'
import api from './services/api'

const CHATS_STORAGE_KEY = 'rag_chats'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [files, setFiles] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking') // 'online', 'offline', 'checking'
  const [chats, setChats] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)

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

  // 채팅 목록 로드
  const loadChats = () => {
    try {
      const saved = localStorage.getItem(CHATS_STORAGE_KEY)
      if (saved) {
        const parsedChats = JSON.parse(saved)
        setChats(parsedChats)
        // 첫 번째 채팅 선택 또는 가장 최근 채팅 선택
        if (parsedChats.length > 0 && !currentChatId) {
          const sortedChats = [...parsedChats].sort((a, b) => 
            new Date(b.updatedAt) - new Date(a.updatedAt)
          )
          setCurrentChatId(sortedChats[0].id)
        }
      }
    } catch (error) {
      console.error('채팅 목록 로드 실패:', error)
    }
  }

  // 채팅 목록 저장
  const saveChats = (updatedChats) => {
    try {
      localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(updatedChats))
      setChats(updatedChats)
    } catch (error) {
      console.error('채팅 목록 저장 실패:', error)
    }
  }

  // 새 채팅 생성
  const handleNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: '새 채팅',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastMessage: null
    }
    const updatedChats = [newChat, ...chats]
    saveChats(updatedChats)
    setCurrentChatId(newChat.id)
  }

  // 채팅 선택
  const handleSelectChat = (chatId) => {
    setCurrentChatId(chatId)
  }

  // 채팅 삭제
  const handleDeleteChat = (chatId) => {
    const updatedChats = chats.filter(chat => chat.id !== chatId)
    saveChats(updatedChats)
    
    // 삭제된 채팅이 현재 채팅이면 다른 채팅 선택
    if (currentChatId === chatId) {
      if (updatedChats.length > 0) {
        setCurrentChatId(updatedChats[0].id)
      } else {
        setCurrentChatId(null)
      }
    }
  }

  // 메시지 변경 처리
  const handleMessagesChange = (newMessages) => {
    if (!currentChatId) return
    
    const updatedChats = chats.map(chat => {
      if (chat.id === currentChatId) {
        const lastMessage = newMessages.length > 0 
          ? (newMessages[newMessages.length - 1].content || '').substring(0, 50)
          : null
        
        // 첫 메시지가 있으면 채팅 제목 업데이트
        let title = chat.title
        if (title === '새 채팅' && newMessages.length > 0) {
          const firstUserMessage = newMessages.find(m => m.role === 'user')
          if (firstUserMessage) {
            title = firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '')
          }
        }
        
        return {
          ...chat,
          messages: newMessages,
          title,
          lastMessage,
          updatedAt: new Date().toISOString()
        }
      }
      return chat
    })
    saveChats(updatedChats)
  }

  // 현재 채팅의 메시지 가져오기
  const getCurrentMessages = () => {
    const currentChat = chats.find(chat => chat.id === currentChatId)
    return currentChat ? currentChat.messages : []
  }

  useEffect(() => {
    // 초기 상태 확인
    checkBackendStatus()
    loadFiles()
    loadChats()

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
          <div className="chat-container">
            <ChatSidebar
              chats={chats}
              currentChatId={currentChatId}
              onSelectChat={handleSelectChat}
              onNewChat={handleNewChat}
              onDeleteChat={handleDeleteChat}
            />
            <div className="chat-main">
              {currentChatId ? (
                <ChatInterface
                  backendStatus={backendStatus}
                  chatId={currentChatId}
                  messages={getCurrentMessages()}
                  onMessagesChange={handleMessagesChange}
                />
              ) : (
                <div className="chat-welcome">
                  <h2>채팅을 시작하세요</h2>
                  <p>새 채팅 버튼을 클릭하여 대화를 시작하세요.</p>
                </div>
              )}
            </div>
          </div>
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


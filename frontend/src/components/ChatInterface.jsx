import React, { useState, useRef, useEffect } from 'react'
import './ChatInterface.css'
import api from '../services/api'

function ChatInterface({ backendStatus }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    
    // 백엔드가 연결되지 않은 경우 경고
    if (backendStatus === 'offline') {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.',
          error: true
        }
      ])
      return
    }

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.post('/query', {
        query: userMessage
      })

      const { answer, sources, has_answer } = response.data

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: answer,
          sources: sources || [],
          has_answer: has_answer
        }
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `오류가 발생했습니다: ${error.response?.data?.error || error.message}`,
          error: true
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <h2>안녕하세요! 👋</h2>
            {backendStatus === 'offline' ? (
              <>
                <p style={{ color: '#f44336', fontWeight: 'bold' }}>
                  ⚠️ 백엔드 서버에 연결할 수 없습니다
                </p>
                <p className="chat-hint">
                  백엔드 서버가 실행 중인지 확인해주세요.
                  <br />
                  <code>cd backend && python app.py</code>
                </p>
              </>
            ) : (
              <>
                <p>질문을 입력하여 문서 기반 답변을 받아보세요.</p>
                <p className="chat-hint">
                  💡 업로드된 문서의 내용만 답변에 포함됩니다.
                </p>
              </>
            )}
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'user' ? (
                <div className="message-bubble user">
                  {msg.content}
                </div>
              ) : (
                <div className={`message-bubble assistant ${msg.error ? 'error' : ''}`}>
                  <div className="message-text">{msg.content}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="message-sources">
                      <h4>📄 출처:</h4>
                      {msg.sources.map((source, i) => (
                        <div key={i} className="source-item">
                          <span className="source-filename">{source.filename}</span>
                          <span className="source-page">페이지 {source.page}</span>
                          {source.type === 'table' && (
                            <span className="source-type">[표]</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="message-bubble assistant">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={backendStatus === 'offline' ? '백엔드 연결이 필요합니다...' : '질문을 입력하세요...'}
          disabled={loading || backendStatus === 'offline'}
        />
        <button
          type="submit"
          className="chat-submit"
          disabled={loading || !input.trim() || backendStatus === 'offline'}
          title={backendStatus === 'offline' ? '백엔드 서버에 연결할 수 없습니다' : ''}
        >
          전송
        </button>
      </form>
    </div>
  )
}

export default ChatInterface


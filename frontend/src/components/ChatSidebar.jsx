import React from 'react'
import './ChatSidebar.css'

function ChatSidebar({ chats, currentChatId, onSelectChat, onNewChat, onDeleteChat }) {
  return (
    <div className="chat-sidebar">
      <div className="chat-sidebar-header">
        <button className="new-chat-button" onClick={onNewChat} title="새 채팅">
          ➕ 새 채팅
        </button>
      </div>
      
      <div className="chat-list">
        {chats.length === 0 ? (
          <div className="chat-list-empty">
            <p>채팅이 없습니다</p>
            <p className="chat-list-hint">새 채팅을 만들어 시작하세요</p>
          </div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className="chat-item-content">
                <div className="chat-item-title">{chat.title}</div>
                <div className="chat-item-preview">
                  {chat.lastMessage || '새 채팅'}
                </div>
                <div className="chat-item-date">
                  {new Date(chat.updatedAt).toLocaleDateString('ko-KR', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
              <button
                className="chat-item-delete"
                onClick={(e) => {
                  e.stopPropagation()
                  if (window.confirm(`"${chat.title}" 채팅을 삭제하시겠습니까?`)) {
                    onDeleteChat(chat.id)
                  }
                }}
                title="채팅 삭제"
              >
                🗑️
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ChatSidebar


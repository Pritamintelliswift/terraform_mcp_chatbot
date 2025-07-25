import React, { useState, useEffect } from 'react';
import './Sidebar.css';

interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  preview: string;
}

interface SidebarProps {
  currentChatId: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat
}) => {
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    const fetchChatSessions = async () => {
      try {
        const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api/chat";
        const response = await fetch(`${API_URL}/sessions`);
        if (response.ok) {
          const sessions = await response.json();
          const formattedSessions = sessions.map((session: any) => ({
            id: session.id,
            title: session.title || 'New Chat',
            timestamp: new Date(session.timestamp),
            preview: session.preview || ''
          }));
          setChatSessions(formattedSessions);
        }
      } catch (error) {
        console.error('Failed to fetch chat sessions:', error);
        // Keep empty array on error
      }
    };

    fetchChatSessions();
  }, []);

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <span className="icon">+</span>
          {!isCollapsed && <span>New chat</span>}
        </button>
        <button 
          className="collapse-btn" 
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          <span className="icon">{isCollapsed ? '→' : '←'}</span>
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div className="sidebar-section">
            <h3>Recent</h3>
          </div>

          <div className="chat-list">
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className={`chat-item ${currentChatId === session.id ? 'active' : ''}`}
                onClick={() => onSelectChat(session.id)}
              >
                <div className="chat-item-content">
                  <div className="chat-title">{session.title}</div>
                  <div className="chat-preview">{session.preview}</div>
                  <div className="chat-timestamp">{formatTimestamp(session.timestamp)}</div>
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(session.id);
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          <div className="sidebar-footer">
            <div className="user-info">
              <div className="user-avatar">👤</div>
              <div className="user-name">User</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Sidebar;
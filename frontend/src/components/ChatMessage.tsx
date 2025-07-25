import React from 'react';
import './ChatMessage.css';

interface ChatMessageProps {
  isUser: boolean;
  message: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ isUser, message }) => {
  return (
    <div className={`message-wrapper ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-container">
        <div className="message-avatar">
          {isUser ? (
            <div className="user-avatar">U</div>
          ) : (
            <div className="assistant-avatar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
          )}
        </div>
        <div className="message-content">
          <div className="message-text">{message}</div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
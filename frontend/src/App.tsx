import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import { log } from 'console';

const App: React.FC = () => {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [chatSessions, setChatSessions] = useState<any[]>([]);

  const handleNewChat = () => {
    const newChatId = `chat-${Date.now()}`;
    setCurrentChatId(newChatId);
    // Clear current messages for new chat
  };
//console.log(Date.now(),"date");

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    // Load messages for selected chat
  };

  const handleDeleteChat = (chatId: string) => {
    setChatSessions(prev => prev.filter(chat => chat.id !== chatId));
    if (currentChatId === chatId) {
      setCurrentChatId(null);
    }
  };

  return (
    <div className="app">
      <Sidebar
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />
      <div className="main-content">
        <div className="chat-header">
          <h1>Gemini</h1>
          <div className="model-info">
            <span className="model-badge">GPT-4</span>
          </div>
        </div>
        <Chat key={currentChatId} chatId={currentChatId} />
      </div>
    </div>
  );
};

export default App;
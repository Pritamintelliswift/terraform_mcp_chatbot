import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import "./Chat.css";

interface Message {
  user: string;
  bot: string;
}

interface ChatProps {
  chatId: string | null;
}

// API configuration
const API_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5000/api/chat";

const Chat: React.FC<ChatProps> = ({ chatId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch chat history on component mount or when chatId changes
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!chatId) {
        setMessages([]);
        return;
      }

      try {
        const response = await axios.get(`${API_URL}/history/${chatId}`);
        if (response.data && Array.isArray(response.data)) {
          setMessages(response.data);
        }
      } catch (err) {
        console.error("Failed to fetch chat history:", err);
        // Don't show error to user on initial load
      }
    };

    fetchChatHistory();
  }, [chatId]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (message: string) => {
    try {
      // Set loading state and clear any previous errors
      setLoading(true);
      setError(null);

      // Create a temporary message object to show immediately
      const tempMessage: Message = {
        user: message,
        bot: "",
      };

      // Add user message to the chat immediately for better UX
      setMessages((prevMessages) => [...prevMessages, { ...tempMessage }]);

      // Generate chatId if not provided
      const currentChatId = chatId || `chat-${Date.now()}`;

      // Send the message to the backend API
      const response = await axios.post(API_URL, { 
        message, 
        chatId: currentChatId 
      });

      // Update the message with the bot's response
      if (response.data && response.data.reply) {
        setMessages((prevMessages) => {
          // Replace the last message with the complete conversation
          const updatedMessages = [...prevMessages];
          updatedMessages[updatedMessages.length - 1] = {
            user: message,
            bot: response.data.reply,
          };
          return updatedMessages;
        });
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err: any) {
      console.error("Error sending message:", err);

      // Show error message to user
      setError(
        axios.isAxiosError(err) && err.response
          ? `Server error: ${err.response.status} - ${
              err.response.data?.error || "Unknown error"
            }`
          : "Failed to connect to the server. Please try again later."
      );

      // Remove the temporary message if there was an error
      setMessages((prevMessages) => prevMessages.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>No messages yet. Start a conversation!</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <React.Fragment key={index}>
              <ChatMessage isUser={true} message={msg.user} />
              <ChatMessage isUser={false} message={msg.bot} />
            </React.Fragment>
          ))
        )}
        {loading && (
          <div className="loading-indicator">
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
          </div>
        )}
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
};

export default Chat;

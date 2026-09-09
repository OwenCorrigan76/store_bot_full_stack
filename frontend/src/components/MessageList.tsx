import React from "react"
import "../styles/MessageList.css"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: string
}

interface MessageListProps {
  messages: Message[]
  loading: boolean
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div key={index} className={`message message-${message.role}`}>
          <div className="message-avatar">
            {message.role === "user" ? "👤" : "🎸"}
          </div>
          <div className="message-content">
            <div className="message-text">{message.content}</div>
            <div className="message-time">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}

      {loading && (
        <div className="message message-assistant">
          <div className="message-avatar">🎸</div>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList

import React, { useState, useRef, useEffect } from "react"
import axios from "axios"
import MessageList from "./MessageList"
import InputBox from "./InputBox"
import "../styles/ChatInterface.css"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: string
}

interface ChatInterfaceProps {
  conversationId: string
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ conversationId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! 👋 Welcome to our guitar store. Ask me about any guitars you're interested in. I can help you find the right instrument!",
      timestamp: new Date().toISOString(),
    },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (userMessage: string) => {
    if (!userMessage.trim()) return

    // Add user message to chat
    const newUserMessage: Message = {
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, newUserMessage])
    setLoading(true)
    setError(null)

    try {
      // Send to backend
      const response = await axios.post(
        "http://localhost:8001/api/chat",
        {
          message: userMessage,
          conversation_id: conversationId,
          include_sources: true,
        },
        {
          timeout: 60000, // 60 second timeout for LLM generation
        }
      )

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : err instanceof Error
            ? err.message
            : "Failed to get response from the server"

      setError(errorMessage)
      console.error("Chat error:", err)

      // Add error message to chat
      const errorAssistantMessage: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorAssistantMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <MessageList messages={messages} loading={loading} />
      <div ref={messagesEndRef} />

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <InputBox
        onSendMessage={handleSendMessage}
        disabled={loading}
        placeholder="Ask about our guitars... (e.g., 'How much is a Fender Stratocaster?')"
      />
    </div>
  )
}

export default ChatInterface

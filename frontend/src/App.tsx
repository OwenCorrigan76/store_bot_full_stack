import { useState, useEffect } from "react"
import ChatInterface from "./components/ChatInterface"
import "./App.css"

function App() {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "error">(
    "checking"
  )

  // Check if backend API is available
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch("http://localhost:8001/health")
        if (response.ok) {
          setApiStatus("connected")
          // Generate a new conversation ID
          setConversationId(`conv_${Date.now()}`)
        }
      } catch (error) {
        console.error("API check failed:", error)
        setApiStatus("error")
      }
    }

    checkApi()
    const interval = setInterval(checkApi, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎸 Guitar Store Chatbot</h1>
        <p className="tagline">Ask us about our guitars!</p>
        <div className={`status ${apiStatus}`}>
          {apiStatus === "checking" && "⏳ Checking..."}
          {apiStatus === "connected" && "✅ Connected"}
          {apiStatus === "error" && "❌ Backend unavailable"}
        </div>
      </header>

      <main className="app-main">
        {apiStatus === "error" ? (
          <div className="error-banner">
            <h2>⚠️ Backend Not Available</h2>
            <p>
              Make sure the FastAPI backend is running on{" "}
              <code>http://localhost:8001</code>
            </p>
            <p>
              Start it with: <code>cd backend && uvicorn main:app --reload</code>
            </p>
          </div>
        ) : conversationId ? (
          <ChatInterface conversationId={conversationId} />
        ) : (
          <div className="loading">Loading...</div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Powered by Llama 3.1 • vLLM • FastAPI • React{" "}
          <span className="version">v1.0</span>
        </p>
      </footer>
    </div>
  )
}

export default App

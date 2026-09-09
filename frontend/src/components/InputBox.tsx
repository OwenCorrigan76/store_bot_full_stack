import React, { useState } from "react"
import "../styles/InputBox.css"

interface InputBoxProps {
  onSendMessage: (message: string) => void
  disabled: boolean
  placeholder?: string
}

const InputBox: React.FC<InputBoxProps> = ({
  onSendMessage,
  disabled,
  placeholder = "Type a message...",
}) => {
  const [input, setInput] = useState("")

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input)
      setInput("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-box">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        className="input-field"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="send-button"
      >
        {disabled ? "..." : "Send"}
      </button>
    </div>
  )
}

export default InputBox

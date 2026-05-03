import { useState, useRef, useEffect } from 'react'
import logo from './assets/logo.png'
import './App.css'

const SESSION_ID = 'session_' + Math.random().toString(36).slice(2)

function Message({ msg }) {
  return (
    <div className={`msg ${msg.role}`}>
      <div className="bubble">{msg.text}</div>
      {msg.sources?.length > 0 && (
        <div className="sources">
          Sources:{' '}
          {msg.sources.map((s, i) => (
            <a key={i} href={s.url} target="_blank" rel="noreferrer">
              {s.section || s.url}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi! I\'m the TopNeurons AI Assistant. Ask me about admissions, eligibility, benefits, and more.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function send() {
    const query = input.trim()
    if (!query || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: query }])
    setLoading(true)
    try {
      const BACKEND = import.meta.env.VITE_API_URL || ''
      const res = await fetch(`${BACKEND}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: SESSION_ID }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'bot',
        text: data.answer || data.error || 'Something went wrong.',
        sources: data.sources || [],
      }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Connection error. Make sure the backend is running.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <img src={logo} alt="TopNeurons" className="header-logo" />
        <div className="header-text">
          <h2>TopNeurons Foundation</h2>
          <p>AI Assistant</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => <Message key={i} msg={msg} />)}
        {loading && (
          <div className="msg bot">
            <div className="bubble typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type your question..."
          disabled={loading}
          autoFocus
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          &#9658;
        </button>
      </div>
    </div>
  )
}

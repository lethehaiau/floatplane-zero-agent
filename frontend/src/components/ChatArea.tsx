import { useState, useEffect, useRef, useCallback } from 'react'
import type { Session } from '../types/session'
import type { Message } from '../types/message'
import { chatApi, sessionsApi } from '../services/api'
import { Markdown } from './Markdown'

interface ChatAreaProps {
  session: Session
  initialMessage?: string | null
  onInitialMessageSent?: () => void
  onSessionUpdate?: (session: Session) => void
}

export function ChatArea({ session, initialMessage, onInitialMessageSent, onSessionUpdate }: ChatAreaProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [streamingContent, setStreamingContent] = useState('')
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleInput, setTitleInput] = useState(session.title)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<(() => void) | null>(null)
  const titleInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    loadMessages()
  }, [session.id])

  // Handle initial message from empty state
  useEffect(() => {
    if (initialMessage) {
      sendPendingMessage(initialMessage)
      onInitialMessageSent?.()
    }
  }, [initialMessage])

  const sendPendingMessage = (messageText: string) => {
    if (!messageText.trim() || loading) return

    setLoading(true)
    setError(null)
    setStreamingContent('')

    abortRef.current = chatApi.streamMessage(
      {
        session_id: session.id,
        message: messageText,
      },
      (message) => setMessages((prev) => [...prev, message]),
      (chunk) => setStreamingContent((prev) => prev + chunk),
      (message) => {
        setStreamingContent('')
        setMessages((prev) => [...prev, message])
        setLoading(false)
        abortRef.current = null
      },
      (errorMsg) => {
        setError(errorMsg)
        setStreamingContent('')
        setLoading(false)
        abortRef.current = null
      }
    )
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent])

  // Cleanup on unmount or session change
  useEffect(() => {
    return () => {
      if (abortRef.current) {
        abortRef.current()
      }
    }
  }, [session.id])

  const loadMessages = async () => {
    try {
      setError(null)
      const data = await chatApi.getSessionMessages(session.id)
      setMessages(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages')
    }
  }

  const handleSend = useCallback(() => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)
    setError(null)
    setStreamingContent('')

    // Abort any previous stream
    if (abortRef.current) {
      abortRef.current()
    }

    abortRef.current = chatApi.streamMessage(
      {
        session_id: session.id,
        message: userMessage,
      },
      // onUserMessage
      (message) => {
        setMessages((prev) => [...prev, message])
      },
      // onContentDelta
      (chunk) => {
        setStreamingContent((prev) => prev + chunk)
      },
      // onDone
      (message) => {
        setStreamingContent('')
        setMessages((prev) => [...prev, message])
        setLoading(false)
        abortRef.current = null
      },
      // onError
      (errorMsg) => {
        setError(errorMsg)
        setStreamingContent('')
        setLoading(false)
        setInput(userMessage) // Restore input on error
        abortRef.current = null
      }
    )
  }, [input, loading, session.id])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Reset title input when session changes
  useEffect(() => {
    setTitleInput(session.title)
    setEditingTitle(false)
  }, [session.id, session.title])

  const handleTitleClick = () => {
    setEditingTitle(true)
    setTimeout(() => titleInputRef.current?.focus(), 0)
  }

  const handleTitleSave = async () => {
    if (titleInput.trim() && titleInput !== session.title) {
      try {
        const updated = await sessionsApi.updateTitle(session.id, titleInput.trim())
        onSessionUpdate?.(updated)
      } catch (err) {
        console.error('Failed to update title:', err)
        setTitleInput(session.title) // Revert on error
      }
    }
    setEditingTitle(false)
  }

  const handleTitleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleTitleSave()
    } else if (e.key === 'Escape') {
      setTitleInput(session.title)
      setEditingTitle(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Header */}
      <div className="px-10 py-5 border-b border-gray-200">
        {editingTitle ? (
          <input
            ref={titleInputRef}
            type="text"
            value={titleInput}
            onChange={(e) => setTitleInput(e.target.value)}
            onBlur={handleTitleSave}
            onKeyDown={handleTitleKeyDown}
            className="text-base font-medium text-gray-900 bg-transparent border-b border-gray-900 outline-none w-full"
          />
        ) : (
          <h2
            onClick={handleTitleClick}
            className="text-base font-medium text-gray-900 cursor-pointer hover:text-gray-600"
            title="Click to edit title"
          >
            {session.title}
          </h2>
        )}
        <p className="text-xs text-gray-500 mt-0.5">
          {session.llm_model}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-10 py-10">
        {messages.length === 0 && !loading && (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-base">No messages yet</p>
            <p className="text-sm mt-1">Start a conversation by typing a message below</p>
          </div>
        )}

        <div className="space-y-7 max-w-3xl">
          {messages.map((message) => (
            <div key={message.id}>
              {message.role === 'user' ? (
                <div className="flex justify-end">
                  <div className="bg-gray-100 px-5 py-4 max-w-md">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1.5 text-right">You</div>
                    <div className="text-gray-900 whitespace-pre-wrap break-words">{message.content}</div>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1.5">Assistant</div>
                  <div className="text-gray-900 leading-relaxed">
                    <Markdown content={message.content} />
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1.5">Assistant</div>
              {streamingContent ? (
                <div className="text-gray-900 leading-relaxed">
                  <Markdown content={streamingContent} />
                  <span className="animate-pulse">▊</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 py-2">
                  <div className="w-1 h-1 bg-gray-500 rounded-full typing-dot"></div>
                  <div className="w-1 h-1 bg-gray-500 rounded-full typing-dot"></div>
                  <div className="w-1 h-1 bg-gray-500 rounded-full typing-dot"></div>
                </div>
              )}
            </div>
          )}
        </div>

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-10 py-2 bg-red-50 border-t border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Input */}
      <div className="px-10 py-6 border-t border-gray-200">
        <div className="flex items-end gap-4 max-w-3xl">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message"
            disabled={loading}
            rows={1}
            className="flex-1 py-3 border-b border-gray-300 focus:border-gray-900 bg-transparent text-gray-900 placeholder-gray-400 focus:outline-none resize-none transition-colors"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="px-6 py-3 bg-gray-900 text-white text-sm hover:opacity-80 disabled:bg-gray-300 disabled:cursor-not-allowed transition-opacity"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

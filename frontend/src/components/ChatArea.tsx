import { useState, useEffect, useRef, useCallback } from 'react'
import type { Session } from '../types/session'
import type { Message } from '../types/message'
import { chatApi, sessionsApi, filesApi, type FileInfo } from '../services/api'
import { Markdown } from './Markdown'
import { FileList } from './FileList'
import { getSessionDraft, saveSessionDraft, clearSessionDraft } from '../utils/draftStorage'

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
  const [files, setFiles] = useState<FileInfo[]>([])
  const [uploadingFile, setUploadingFile] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<(() => void) | null>(null)
  const titleInputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const inputRef = useRef(input)
  const filesRef = useRef(files)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Keep refs in sync with current state
  useEffect(() => {
    inputRef.current = input
  }, [input])

  useEffect(() => {
    filesRef.current = files
  }, [files])

  useEffect(() => {

    const loadData = async () => {
      await loadMessages()

      // Load draft for this session
      const draft = getSessionDraft(session.id)

      if (draft) {
        // Restore draft message
        setInput(draft.message)

        // Restore draft files by loading from backend
        try {
          const allFiles = await filesApi.list(session.id)
          const draftFiles = allFiles.filter(f => draft.fileIds.includes(f.id))
          setFiles(draftFiles)
        } catch (err) {
          console.error('Failed to load draft files:', err)
          setFiles([])
        }
      }
      else {
        setInput('')
        setFiles([])
      }
    }
    loadData()

    // Save draft when exiting this session (cleanup function)
    return () => {
      saveSessionDraft(session.id, {
        message: inputRef.current,
        fileIds: filesRef.current.map(f => f.id)
      })
    }
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

    const filesSnapshot = [...files]
    setLoading(true)
    setError(null)
    setStreamingContent('')

    abortRef.current = chatApi.streamMessage(
      {
        session_id: session.id,
        message: messageText,
        files_metadata: files.map(f => ({
          filename: f.filename,
          file_type: f.file_type
        }))
      },
      (message) => {
        setMessages((prev) => [...prev, message])
        // Clear files from input area after sending
        setFiles([])
        // Clear draft after successful send
        clearSessionDraft(session.id)
      },
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
        setFiles(filesSnapshot) // Restore files on error
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

  const loadMessages = async (): Promise<Message[]> => {
    try {
      setError(null)
      const data = await chatApi.getSessionMessages(session.id)
      setMessages(data)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages')
      return []
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    // Reset input value so same file can be selected again
    e.target.value = ''

    // Validate file type
    const ext = selectedFile.name.split('.').pop()?.toLowerCase()
    if (!ext || !['pdf', 'txt', 'md'].includes(ext)) {
      setError('Only PDF, TXT, and MD files are supported')
      return
    }

    // Validate file size (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    // Check file count (max 3)
    if (files.length >= 3) {
      setError('Maximum 3 files per session')
      return
    }

    try {
      setUploadingFile(true)
      setError(null)
      const uploadedFile = await filesApi.upload(session.id, selectedFile)
      setFiles((prev) => [...prev, uploadedFile])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file')
    } finally {
      setUploadingFile(false)
    }
  }

  const handleFileDelete = async (fileId: string) => {
    try {
      setError(null)
      await filesApi.delete(session.id, fileId)
      setFiles((prev) => prev.filter((f) => f.id !== fileId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file')
    }
  }

  const handleSend = useCallback(() => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    const filesSnapshot = [...files]
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
        files_metadata: files.map(f => ({
          filename: f.filename,
          file_type: f.file_type
        }))
      },
      // onUserMessage
      (message) => {
        setMessages((prev) => [...prev, message])
        // Clear files from input area after sending
        setFiles([])
        // Clear draft after successful send
        clearSessionDraft(session.id)
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
        setFiles(filesSnapshot) // Restore files on error
        abortRef.current = null
      }
    )
  }, [input, loading, session.id, files])

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
                    {message.message_metadata?.files && message.message_metadata.files.length > 0 && (
                      <div className="mb-3">
                        <div className="flex flex-wrap gap-2">
                          {message.message_metadata.files.map((file, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg text-sm border border-gray-200"
                            >
                              <div className="flex items-center justify-center w-10 h-10 bg-gray-100 rounded text-xs font-medium text-gray-600">
                                {file.file_type.toUpperCase()}
                              </div>
                              <span className="text-gray-500">{file.filename}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
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
        <div className="max-w-3xl">
          {/* File List */}
          <FileList files={files} onDelete={handleFileDelete} />

          {/* Input Area */}
          <div className="flex items-end gap-4">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Paperclip button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || uploadingFile || files.length >= 3}
              className="pb-3 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title={files.length >= 3 ? 'Maximum 3 files per session' : 'Upload file (PDF, TXT, MD)'}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                />
              </svg>
            </button>

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
    </div>
  )
}

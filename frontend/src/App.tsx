import { useState, useEffect, useRef } from 'react'
import { SessionSidebar, type SessionSidebarRef } from './components/SessionSidebar'
import { ChatArea } from './components/ChatArea'
import { modelsApi, sessionsApi, type ModelInfo } from './services/api'
import type { Session } from './types/session'
import floatplaneFront from './assets/floatplane-front.png';

// Default models to show immediately (prevents flicker during loading)
const DEFAULT_MODELS: ModelInfo[] = [
  {
    provider: "openai",
    model: "gpt-4",
    display_name: "OpenAI / GPT-4"
  },
  {
    provider: "anthropic",
    model: "claude-sonnet-4-20250514",
    display_name: "Anthropic / Claude Sonnet 4"
  },
  {
    provider: "google",
    model: "gemini/gemini-2.5-flash",
    display_name: "Google / Gemini 2.5 Flash"
  }
]

function App() {
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [models, setModels] = useState<ModelInfo[]>(DEFAULT_MODELS)
  const [selectedModel, setSelectedModel] = useState<ModelInfo | null>(DEFAULT_MODELS[0])
  const [message, setMessage] = useState('')
  const [creating, setCreating] = useState(false)
  const [initialMessage, setInitialMessage] = useState<string | null>(null)
  const sidebarRef = useRef<SessionSidebarRef>(null)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      const response = await modelsApi.list()
      setModels(response.models)
      if (response.models.length > 0) {
        setSelectedModel(response.models[0])
      } else {
        // API succeeded but returned no models (no API keys configured)
        // Clear default models to show error message
        setSelectedModel(null)
      }
    } catch (err) {
      console.error('Failed to load models:', err)
      // On error, clear models to show error message
      setModels([])
      setSelectedModel(null)
    }
  }

  const handleStartChat = async () => {
    if (!message.trim() || !selectedModel || creating) return

    const messageToSend = message.trim()
    setCreating(true)
    try {
      // Create session with first message as title (truncated)
      const title = messageToSend.slice(0, 50)
      const session = await sessionsApi.create({
        title,
        llm_provider: selectedModel.provider,
        llm_model: selectedModel.model,
      })

      // Set the initial message before selecting session
      // This ensures ChatArea receives it when it mounts
      setInitialMessage(messageToSend)
      setMessage('')

      // Select the new session (this will mount ChatArea)
      setSelectedSession(session)

      // Refresh sidebar to show new session
      sidebarRef.current?.refreshSessions()
    } catch (err) {
      console.error('Failed to create session:', err)
    } finally {
      setCreating(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleStartChat()
    }
  }

  return (
    <div className="flex h-screen">
      {/* Session Sidebar */}
      <SessionSidebar
        ref={sidebarRef}
        onSessionSelect={setSelectedSession}
        selectedSessionId={selectedSession?.id}
      />

      {/* Main Content */}
      {selectedSession ? (
        <ChatArea
          session={selectedSession}
          initialMessage={initialMessage}
          onInitialMessageSent={() => setInitialMessage(null)}
          onSessionUpdate={(updated) => {
            setSelectedSession(updated)
            sidebarRef.current?.refreshSessions()
          }}
        />
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center bg-white">
          <div className="w-full max-w-lg px-6">
            {/* Logo and Title */}
            <div className="flex flex-col items-center mb-12">
              <img src={floatplaneFront} alt="Floatplane" width="80" className="mb-4" />
              <h1 className="text-xl font-medium text-gray-900">
                Start a conversation
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Type a message below to begin
              </p>
            </div>

            {/* Input with inline model selector */}
            <div className="w-full">
              <div className="flex items-center gap-4 border-b border-gray-300 focus-within:border-gray-900 transition-colors">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message"
                  disabled={creating || models.length === 0}
                  className="flex-1 py-4 text-base bg-transparent focus:outline-none placeholder-gray-400"
                />
                <select
                  value={selectedModel ? `${selectedModel.provider}:${selectedModel.model}` : ''}
                  onChange={(e) => {
                    const [provider, model] = e.target.value.split(':')
                    const found = models.find(m => m.provider === provider && m.model === model)
                    setSelectedModel(found || null)
                  }}
                  className="text-sm text-gray-500 bg-transparent border-none focus:outline-none cursor-pointer py-4"
                >
                  {models.map((m) => (
                    <option key={`${m.provider}:${m.model}`} value={`${m.provider}:${m.model}`}>
                      {m.display_name}
                    </option>
                  ))}
                </select>
              </div>
              <p className="text-xs text-gray-400 mt-4 text-center">
                Press Enter to send
              </p>
            </div>

            {models.length === 0 && (
              <p className="text-center text-red-500 text-sm mt-6">
                No models available. Please configure API keys in the backend.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App

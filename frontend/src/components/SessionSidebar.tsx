import { useState, useEffect, forwardRef, useImperativeHandle } from 'react'
import type { Session } from '../types/session'
import { sessionsApi } from '../services/api'
import floatplaneSide from '../assets/floatplane-side.png';

interface SessionSidebarProps {
  onSessionSelect?: (session: Session | null) => void
  selectedSessionId?: string | null
}

export interface SessionSidebarRef {
  refreshSessions: () => void
}

export const SessionSidebar = forwardRef<SessionSidebarRef, SessionSidebarProps>(
  function SessionSidebar({ onSessionSelect, selectedSessionId }, ref) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadSessions = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await sessionsApi.list()
      setSessions(data.sessions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  useImperativeHandle(ref, () => ({
    refreshSessions: loadSessions,
  }))

  useEffect(() => {
    loadSessions()
  }, [])

  const handleNewChat = () => {
    // Clear selection to show empty state (where user can select model and type message)
    onSessionSelect?.(null)
  }

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this session?')) return

    try {
      await sessionsApi.delete(sessionId)
      setSessions(sessions.filter((s) => s.id !== sessionId))
      if (selectedSessionId === sessionId) {
        onSessionSelect?.(sessions[0])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session')
    }
  }

  const handleCloneSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const clonedSession = await sessionsApi.clone(sessionId)
      setSessions([clonedSession, ...sessions])
      onSessionSelect?.(clonedSession)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clone session')
    }
  }

  return (
    <div className="w-60 bg-white text-gray-900 h-screen flex flex-col border-r border-gray-200">
      {/* Header */}
      <div className="px-5 py-6">
        <img src={floatplaneSide} width={100} className="mb-6" />
        <button
          onClick={handleNewChat}
          className="w-full py-2.5 border border-gray-300 text-gray-900 text-sm font-normal hover:border-gray-900 transition-colors"
        >
          New conversation
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-3">
        {loading && (
          <div className="text-gray-500 text-center py-4 text-sm">Loading sessions...</div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm mx-2">
            {error}
          </div>
        )}

        {!loading && sessions.length === 0 && (
          <div className="text-gray-500 text-center py-4 text-sm">
            No sessions yet
          </div>
        )}

        <div className="space-y-0.5">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSessionSelect?.(session)}
              className={`px-2 py-3 cursor-pointer transition-colors group border-l-2 ${
                selectedSessionId === session.id
                  ? 'border-gray-900 bg-gray-50'
                  : 'border-transparent hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm truncate">{session.title}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {session.llm_model}
                  </p>
                </div>
                <div className="flex gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => handleCloneSession(session.id, e)}
                    className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-900"
                    title="Clone session"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    className="p-1 hover:bg-red-100 rounded text-gray-500 hover:text-red-600"
                    title="Delete session"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-4 text-xs text-gray-400">
        <div>{sessions.length} conversations</div>
      </div>
    </div>
  )
})

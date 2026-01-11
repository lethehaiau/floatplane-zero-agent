/**
 * Per-session draft storage using localStorage.
 *
 * Stores message text and file IDs for each session,
 * allowing users to switch between sessions without losing their work.
 */

export interface SessionDraft {
  message: string
  fileIds: string[]
}

const STORAGE_KEY = 'sessionDrafts'

/**
 * Get all session drafts from localStorage.
 */
function getAllDrafts(): Record<string, SessionDraft> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch (error) {
    console.error('Failed to load drafts from localStorage:', error)
    return {}
  }
}

/**
 * Save all drafts to localStorage.
 */
function saveAllDrafts(drafts: Record<string, SessionDraft>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts))
  } catch (error) {
    console.error('Failed to save drafts to localStorage:', error)
  }
}

/**
 * Get draft for a specific session.
 */
export function getSessionDraft(sessionId: string): SessionDraft | null {
  const drafts = getAllDrafts()
  return drafts[sessionId] || null
}

/**
 * Save draft for a specific session.
 */
export function saveSessionDraft(sessionId: string, draft: SessionDraft) {
  const drafts = getAllDrafts()

  // Only save if there's actual content
  if (draft.message.trim() || draft.fileIds.length > 0) {
    drafts[sessionId] = draft
  } else {
    // Remove empty drafts
    delete drafts[sessionId]
  }

  saveAllDrafts(drafts)
}

/**
 * Clear draft for a specific session.
 */
export function clearSessionDraft(sessionId: string) {
  const drafts = getAllDrafts()
  delete drafts[sessionId]
  saveAllDrafts(drafts)
}

/**
 * Clear all drafts (useful for logout/cleanup).
 */
export function clearAllDrafts() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Failed to clear drafts:', error)
  }
}

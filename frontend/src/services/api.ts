import type { Session, SessionCreate, SessionListResponse } from '../types/session'
import type { ChatRequest, ChatResponse, Message } from '../types/message'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface ModelInfo {
  provider: string
  model: string
  display_name: string
}

export interface ModelsResponse {
  models: ModelInfo[]
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text()
    throw new ApiError(response.status, error || response.statusText)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T
  }

  return response.json()
}

export const modelsApi = {
  async list(): Promise<ModelsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/models`)
    return handleResponse<ModelsResponse>(response)
  },
}

export const sessionsApi = {
  async create(data: SessionCreate): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse<Session>(response)
  },

  async list(): Promise<SessionListResponse> {
    const response = await fetch(`${API_BASE_URL}/api/sessions`)
    return handleResponse<SessionListResponse>(response)
  },

  async get(id: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${id}`)
    return handleResponse<Session>(response)
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${id}`, {
      method: 'DELETE',
    })
    return handleResponse<void>(response)
  },

  async clone(id: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${id}/clone`, {
      method: 'POST',
    })
    return handleResponse<Session>(response)
  },

  async updateTitle(id: string, title: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    })
    return handleResponse<Session>(response)
  },
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    return handleResponse<ChatResponse>(response)
  },

  async getSessionMessages(sessionId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}/api/chat/sessions/${sessionId}/messages`)
    return handleResponse<Message[]>(response)
  },

  streamMessage(
    request: ChatRequest,
    onUserMessage: (message: Message) => void,
    onContentDelta: (chunk: string) => void,
    onDone: (message: Message) => void,
    onError: (error: string) => void
  ): () => void {
    const controller = new AbortController()

    fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const error = await response.text()
          onError(error || response.statusText)
          return
        }

        const reader = response.body?.getReader()
        if (!reader) {
          onError('No response body')
          return
        }

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // Process complete SSE events
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // Keep incomplete line in buffer

          let eventType = ''
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7)
            } else if (line.startsWith('data: ')) {
              const data = line.slice(6)
              try {
                const parsed = JSON.parse(data)
                switch (eventType) {
                  case 'user_message':
                    onUserMessage(parsed as Message)
                    break
                  case 'content_delta':
                    onContentDelta(parsed.chunk)
                    break
                  case 'done':
                    onDone(parsed.message as Message)
                    break
                  case 'error':
                    onError(parsed.detail)
                    break
                }
              } catch {
                // Ignore parse errors for incomplete data
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError(err.message)
        }
      })

    // Return abort function
    return () => controller.abort()
  },
}

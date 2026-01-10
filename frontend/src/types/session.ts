export interface Session {
  id: string
  title: string
  llm_provider: string
  llm_model: string
  created_at: string
  updated_at: string
}

export interface SessionCreate {
  title?: string
  llm_provider: string
  llm_model: string
}

export interface SessionListResponse {
  sessions: Session[]
  total: number
}

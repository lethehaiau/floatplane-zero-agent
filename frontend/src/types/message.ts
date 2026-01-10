export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ChatRequest {
  session_id: string
  message: string
}

export interface ChatResponse {
  user_message: Message
  assistant_message: Message
}

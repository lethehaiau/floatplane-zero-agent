export interface FileMetadata {
  filename: string
  file_type: string
}

export interface MessageMetadata {
  files?: FileMetadata[]
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  message_metadata?: MessageMetadata | null
}

export interface ChatRequest {
  session_id: string
  message: string
  files_metadata?: FileMetadata[]
}

export interface ChatResponse {
  user_message: Message
  assistant_message: Message
}

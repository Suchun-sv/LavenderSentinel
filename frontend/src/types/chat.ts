/**
 * Chat-related TypeScript types
 */

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  paper_ids: string[];
  citations: string[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  paper_context?: string[];
  include_sources?: boolean;
  max_tokens?: number;
}

export interface ChatSource {
  paper_id: string;
  title: string;
  excerpt: string;
  score: number;
}

export interface ChatResponse {
  message: ChatMessage;
  session_id: string;
  sources: ChatSource[];
  suggested_followups: string[];
}

export interface ChatSession {
  id: string;
  title?: string;
  messages: ChatMessage[];
  paper_context: string[];
  created_at: string;
  updated_at: string;
}

export interface StreamingChatChunk {
  chunk: string;
  done: boolean;
  session_id?: string;
  sources?: ChatSource[];
}


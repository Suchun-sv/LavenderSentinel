/**
 * Chat API service
 */

import apiClient from './api';
import type {
  ChatRequest,
  ChatResponse,
  ChatSession,
  StreamingChatChunk,
} from '@/types';

export const chatService = {
  /**
   * Send a chat message and get a response
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/chat', request);
    return response.data;
  },

  /**
   * Stream a chat response using Server-Sent Events
   */
  async streamMessage(
    request: ChatRequest,
    onChunk: (chunk: StreamingChatChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamingChatChunk;
              onChunk(data);
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      if (onError && error instanceof Error) {
        onError(error);
      }
      throw error;
    }
  },

  /**
   * Get list of chat sessions
   */
  async listSessions(userId?: string): Promise<ChatSession[]> {
    const params: Record<string, unknown> = {};
    if (userId) {
      params.user_id = userId;
    }
    
    const response = await apiClient.get<ChatSession[]>('/chat/sessions', { params });
    return response.data;
  },

  /**
   * Get a specific chat session
   */
  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await apiClient.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/chat/sessions/${sessionId}`);
  },

  /**
   * Create a WebSocket connection for real-time chat
   */
  createWebSocket(sessionId: string): WebSocket {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/chat/ws/${sessionId}`;
    return new WebSocket(wsUrl);
  },
};

export default chatService;


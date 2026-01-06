/**
 * Chat store using Zustand
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ChatMessage, ChatSession, ChatSource, MessageRole } from '@/types';
import { chatService } from '@/services';

interface ChatState {
  // State
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  paperContext: string[];
  suggestedFollowups: string[];

  // Actions
  sendMessage: (message: string) => Promise<void>;
  streamMessage: (message: string) => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  createSession: (paperContext?: string[]) => void;
  deleteSession: (sessionId: string) => Promise<void>;
  setPaperContext: (paperIds: string[]) => void;
  addToPaperContext: (paperId: string) => void;
  removeFromPaperContext: (paperId: string) => void;
  clearPaperContext: () => void;
  reset: () => void;
}

const createMessage = (
  role: MessageRole,
  content: string,
  paperIds: string[] = [],
  citations: string[] = []
): ChatMessage => ({
  id: crypto.randomUUID(),
  role,
  content,
  timestamp: new Date().toISOString(),
  paper_ids: paperIds,
  citations,
});

const initialState = {
  currentSession: null,
  sessions: [],
  isLoading: false,
  isStreaming: false,
  error: null,
  paperContext: [],
  suggestedFollowups: [],
};

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        sendMessage: async (message: string) => {
          const { currentSession, paperContext } = get();

          // Add user message immediately
          const userMessage = createMessage('user', message, paperContext);

          if (currentSession) {
            set({
              currentSession: {
                ...currentSession,
                messages: [...currentSession.messages, userMessage],
              },
            });
          }

          set({ isLoading: true, error: null });

          try {
            const response = await chatService.sendMessage({
              message,
              session_id: currentSession?.id,
              paper_context: paperContext,
              include_sources: true,
            });

            set({
              currentSession: {
                id: response.session_id,
                title: currentSession?.title,
                messages: [
                  ...(currentSession?.messages || []),
                  userMessage,
                  response.message,
                ],
                paper_context: paperContext,
                created_at: currentSession?.created_at || new Date().toISOString(),
                updated_at: new Date().toISOString(),
              },
              suggestedFollowups: response.suggested_followups,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to send message',
              isLoading: false,
            });
          }
        },

        streamMessage: async (message: string) => {
          const { currentSession, paperContext } = get();

          // Add user message immediately
          const userMessage = createMessage('user', message, paperContext);

          const updatedSession: ChatSession = currentSession
            ? {
                ...currentSession,
                messages: [...currentSession.messages, userMessage],
              }
            : {
                id: crypto.randomUUID(),
                messages: [userMessage],
                paper_context: paperContext,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              };

          set({
            currentSession: updatedSession,
            isStreaming: true,
            error: null,
          });

          // Create placeholder for assistant message
          const assistantMessage = createMessage('assistant', '');
          let fullContent = '';
          let sources: ChatSource[] = [];

          try {
            await chatService.streamMessage(
              {
                message,
                session_id: currentSession?.id,
                paper_context: paperContext,
                include_sources: true,
              },
              (chunk) => {
                if (chunk.done) {
                  sources = chunk.sources || [];
                  set({
                    currentSession: {
                      ...get().currentSession!,
                      id: chunk.session_id || get().currentSession!.id,
                      messages: [
                        ...get().currentSession!.messages.slice(0, -1),
                        {
                          ...assistantMessage,
                          content: fullContent,
                          paper_ids: sources.map((s) => s.paper_id),
                        },
                      ],
                    },
                    isStreaming: false,
                  });
                } else {
                  fullContent += chunk.chunk;
                  set({
                    currentSession: {
                      ...get().currentSession!,
                      messages: [
                        ...get().currentSession!.messages.slice(0, -1),
                        { ...assistantMessage, content: fullContent },
                      ],
                    },
                  });
                }
              },
              (error) => {
                set({ error: error.message, isStreaming: false });
              }
            );
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Streaming failed',
              isStreaming: false,
            });
          }
        },

        loadSession: async (sessionId: string) => {
          set({ isLoading: true, error: null });

          try {
            const session = await chatService.getSession(sessionId);
            set({
              currentSession: session,
              paperContext: session.paper_context,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to load session',
              isLoading: false,
            });
          }
        },

        loadSessions: async () => {
          set({ isLoading: true, error: null });

          try {
            const sessions = await chatService.listSessions();
            set({ sessions, isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to load sessions',
              isLoading: false,
            });
          }
        },

        createSession: (paperContext?: string[]) => {
          const newSession: ChatSession = {
            id: crypto.randomUUID(),
            messages: [],
            paper_context: paperContext || [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };

          set({
            currentSession: newSession,
            paperContext: paperContext || [],
            suggestedFollowups: [],
          });
        },

        deleteSession: async (sessionId: string) => {
          try {
            await chatService.deleteSession(sessionId);
            set((state) => ({
              sessions: state.sessions.filter((s) => s.id !== sessionId),
              currentSession:
                state.currentSession?.id === sessionId ? null : state.currentSession,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to delete session',
            });
          }
        },

        setPaperContext: (paperIds: string[]) => {
          set({ paperContext: paperIds });
        },

        addToPaperContext: (paperId: string) => {
          set((state) => ({
            paperContext: state.paperContext.includes(paperId)
              ? state.paperContext
              : [...state.paperContext, paperId],
          }));
        },

        removeFromPaperContext: (paperId: string) => {
          set((state) => ({
            paperContext: state.paperContext.filter((id) => id !== paperId),
          }));
        },

        clearPaperContext: () => {
          set({ paperContext: [] });
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessions: state.sessions,
          paperContext: state.paperContext,
        }),
      }
    ),
    { name: 'chat-store' }
  )
);

export default useChatStore;


/**
 * Full-page chat component
 */

import { useState, useRef, useEffect, type FormEvent } from 'react';
import { Send, Sparkles, Plus, Trash2, FileText } from 'lucide-react';
import { Button, Input, Card, Badge } from '@/components/ui';
import { ChatMessage } from '@/components/chat';
import { useChatStore, usePaperStore } from '@/stores';
import { cn } from '@/lib/utils';

export function ChatPage() {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    currentSession,
    sessions,
    isLoading,
    isStreaming,
    suggestedFollowups,
    paperContext,
    streamMessage,
    createSession,
    loadSession,
    deleteSession,
    removeFromPaperContext,
  } = useChatStore();

  const { papers } = usePaperStore();

  // Get paper titles for context display
  const contextPapers = papers.filter((p) => paperContext.includes(p.id));

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  // Create session if none exists
  useEffect(() => {
    if (!currentSession) {
      createSession();
    }
  }, [currentSession, createSession]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading || isStreaming) return;

    const userMessage = message;
    setMessage('');
    await streamMessage(userMessage);
  };

  const handleSuggestionClick = async (suggestion: string) => {
    if (isLoading || isStreaming) return;
    await streamMessage(suggestion);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Sessions Sidebar */}
      <div className="hidden lg:block w-64 flex-shrink-0">
        <Card className="h-full flex flex-col">
          <div className="p-4 border-b border-[rgb(var(--border))]">
            <Button
              onClick={() => createSession()}
              className="w-full"
              size="sm"
            >
              <Plus className="h-4 w-4" />
              New Chat
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => loadSession(session.id)}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-lg text-sm',
                  'hover:bg-[rgb(var(--muted))] transition-colors',
                  'flex items-center justify-between group',
                  currentSession?.id === session.id && 'bg-lavender-100 dark:bg-lavender-900/30'
                )}
              >
                <span className="truncate">
                  {session.title || 'New Chat'}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <Card className="flex-1 flex flex-col overflow-hidden">
          {/* Paper Context */}
          {contextPapers.length > 0 && (
            <div className="p-4 border-b border-[rgb(var(--border))] bg-lavender-50 dark:bg-lavender-900/10">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-lavender-600" />
                <span className="text-sm font-medium">Papers in context:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {contextPapers.map((paper) => (
                  <Badge
                    key={paper.id}
                    variant="primary"
                    className="flex items-center gap-1"
                  >
                    {paper.title.slice(0, 30)}...
                    <button
                      onClick={() => removeFromPaperContext(paper.id)}
                      className="ml-1 hover:text-red-500"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {currentSession?.messages.length === 0 && (
              <div className="text-center py-12">
                <Sparkles className="h-16 w-16 mx-auto text-lavender-400 mb-6" />
                <h2 className="text-2xl font-display font-bold mb-3">
                  How can I help you today?
                </h2>
                <p className="text-[rgb(var(--muted-foreground))] max-w-md mx-auto mb-8">
                  I can help you understand research papers, explain complex concepts,
                  compare methodologies, and find insights across your collection.
                </p>

                {/* Starter prompts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                  {[
                    'Summarize the key findings from recent papers on transformers',
                    'What are the main challenges in reinforcement learning?',
                    'Compare different approaches to natural language understanding',
                    'Explain attention mechanisms in simple terms',
                  ].map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(prompt)}
                      className="p-4 rounded-lg border border-[rgb(var(--border))] text-left text-sm
                               hover:border-lavender-400 hover:bg-lavender-50 dark:hover:bg-lavender-900/10
                               transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {currentSession?.messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {(isLoading || isStreaming) && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-lavender-400 to-lavender-600 flex items-center justify-center">
                  <Sparkles className="h-4 w-4 text-white animate-pulse" />
                </div>
                <div className="bg-[rgb(var(--muted))] rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-lavender-500 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-lavender-500 rounded-full animate-bounce [animation-delay:0.1s]" />
                    <span className="w-2 h-2 bg-lavender-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {suggestedFollowups.length > 0 && !isLoading && !isStreaming && (
            <div className="px-6 pb-4 flex flex-wrap gap-2">
              {suggestedFollowups.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-sm px-4 py-2 rounded-full bg-lavender-100 text-lavender-700 
                           dark:bg-lavender-900/30 dark:text-lavender-300
                           hover:bg-lavender-200 dark:hover:bg-lavender-900/50
                           transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            className="p-4 border-t border-[rgb(var(--border))]"
          >
            <div className="flex gap-3">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about your papers..."
                disabled={isLoading || isStreaming}
                className="flex-1"
              />
              <Button
                type="submit"
                disabled={!message.trim() || isLoading || isStreaming}
              >
                <Send className="h-4 w-4" />
                Send
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}

export default ChatPage;


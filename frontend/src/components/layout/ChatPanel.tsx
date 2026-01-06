/**
 * Chat side panel component
 */

import { useState, useRef, useEffect, type FormEvent } from 'react';
import { Send, X, Minimize2, Maximize2, Sparkles } from 'lucide-react';
import { Button, Input, Card } from '@/components/ui';
import { useChatStore } from '@/stores';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

interface ChatPanelProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function ChatPanel({ isOpen = true, onClose }: ChatPanelProps) {
  const [message, setMessage] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    currentSession,
    isLoading,
    isStreaming,
    suggestedFollowups,
    paperContext,
    streamMessage,
    createSession,
  } = useChatStore();

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

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        'fixed right-0 top-0 z-40 h-full w-full sm:w-96 bg-[rgb(var(--card))]',
        'border-l border-[rgb(var(--border))] shadow-xl',
        'flex flex-col transition-all duration-300',
        isMinimized && 'h-14'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[rgb(var(--border))]">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-lavender-500" />
          <span className="font-semibold">AI Assistant</span>
          {paperContext.length > 0 && (
            <span className="text-xs text-[rgb(var(--muted-foreground))]">
              ({paperContext.length} papers)
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMinimized(!isMinimized)}
          >
            {isMinimized ? (
              <Maximize2 className="h-4 w-4" />
            ) : (
              <Minimize2 className="h-4 w-4" />
            )}
          </Button>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {currentSession?.messages.length === 0 && (
              <div className="text-center py-8">
                <Sparkles className="h-12 w-12 mx-auto text-lavender-400 mb-4" />
                <h3 className="font-semibold mb-2">Ask anything about papers</h3>
                <p className="text-sm text-[rgb(var(--muted-foreground))]">
                  I can help you understand research, compare papers, and find insights.
                </p>
              </div>
            )}

            {currentSession?.messages.map((msg) => (
              <div
                key={msg.id}
                className={cn(
                  'flex',
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[85%] rounded-2xl px-4 py-2.5',
                    msg.role === 'user'
                      ? 'bg-lavender-600 text-white'
                      : 'bg-[rgb(var(--muted))]'
                  )}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}

            {(isLoading || isStreaming) && (
              <div className="flex justify-start">
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
            <div className="px-4 pb-2 flex flex-wrap gap-2">
              {suggestedFollowups.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-full bg-lavender-100 text-lavender-700 
                           dark:bg-lavender-900/30 dark:text-lavender-300
                           hover:bg-lavender-200 dark:hover:bg-lavender-900/50
                           transition-colors duration-200"
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
            <div className="flex gap-2">
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
              </Button>
            </div>
          </form>
        </>
      )}
    </div>
  );
}

export default ChatPanel;


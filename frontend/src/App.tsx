/**
 * Main App component
 */

import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Header, Sidebar, ChatPanel } from '@/components/layout';
import { HomePage, SearchPage, PapersPage, ChatPage } from '@/pages';

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[rgb(var(--background))]">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-4 lg:p-6 lg:ml-0">
          <div className="max-w-5xl mx-auto">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/papers" element={<PapersPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/saved" element={<div className="text-center py-12 text-[rgb(var(--muted-foreground))]">Saved papers coming soon...</div>} />
              <Route path="/trending" element={<div className="text-center py-12 text-[rgb(var(--muted-foreground))]">Trending papers coming soon...</div>} />
              <Route path="/settings" element={<div className="text-center py-12 text-[rgb(var(--muted-foreground))]">Settings coming soon...</div>} />
            </Routes>
          </div>
        </main>

        {/* Chat Panel - only show on non-chat pages */}
        <ChatPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />
      </div>

      {/* Floating chat button */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full
                   bg-gradient-to-br from-lavender-500 to-lavender-700
                   text-white shadow-lg shadow-lavender-500/30
                   hover:shadow-xl hover:shadow-lavender-500/40
                   hover:scale-105 transition-all duration-200
                   flex items-center justify-center z-30"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-6 h-6"
          >
            <path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 1 7.92 12.446a9 9 0 0 1 -8.313 5.554a9 9 0 0 1 -6.713 -2.545l-3.287 1.045l1.045 -3.287a9 9 0 0 1 8.955 -13.213z" />
          </svg>
        </button>
      )}
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;


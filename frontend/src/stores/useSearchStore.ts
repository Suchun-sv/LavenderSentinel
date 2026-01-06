/**
 * Search store using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { SearchResult, SearchFilters, SearchResponse } from '@/types';
import { searchService } from '@/services';

interface SearchState {
  // State
  query: string;
  results: SearchResult[];
  total: number;
  tookMs: number;
  filters: SearchFilters;
  isLoading: boolean;
  error: string | null;
  recentSearches: string[];

  // Actions
  search: (query: string, filters?: SearchFilters) => Promise<void>;
  setQuery: (query: string) => void;
  setFilters: (filters: SearchFilters) => void;
  clearFilters: () => void;
  clearResults: () => void;
  addRecentSearch: (query: string) => void;
  clearRecentSearches: () => void;
  reset: () => void;
}

const MAX_RECENT_SEARCHES = 10;

const initialState = {
  query: '',
  results: [],
  total: 0,
  tookMs: 0,
  filters: {},
  isLoading: false,
  error: null,
  recentSearches: [],
};

export const useSearchStore = create<SearchState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      search: async (query: string, filters?: SearchFilters) => {
        if (!query.trim()) {
          set({ results: [], total: 0, tookMs: 0 });
          return;
        }

        const currentFilters = filters ?? get().filters;

        set({ query, isLoading: true, error: null });

        try {
          const response: SearchResponse = await searchService.semanticSearch({
            query,
            top_k: 20,
            filters: currentFilters,
            include_summary: true,
          });

          set({
            results: response.results,
            total: response.total,
            tookMs: response.took_ms,
            isLoading: false,
          });

          // Add to recent searches
          get().addRecentSearch(query);
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Search failed',
            isLoading: false,
          });
        }
      },

      setQuery: (query: string) => {
        set({ query });
      },

      setFilters: (filters: SearchFilters) => {
        set({ filters });
      },

      clearFilters: () => {
        set({ filters: {} });
      },

      clearResults: () => {
        set({ results: [], total: 0, tookMs: 0, query: '' });
      },

      addRecentSearch: (query: string) => {
        set((state) => {
          const trimmedQuery = query.trim();
          if (!trimmedQuery) return state;

          // Remove if already exists, add to front
          const filtered = state.recentSearches.filter(
            (s) => s.toLowerCase() !== trimmedQuery.toLowerCase()
          );

          return {
            recentSearches: [trimmedQuery, ...filtered].slice(0, MAX_RECENT_SEARCHES),
          };
        });
      },

      clearRecentSearches: () => {
        set({ recentSearches: [] });
      },

      reset: () => {
        set(initialState);
      },
    }),
    { name: 'search-store' }
  )
);

export default useSearchStore;


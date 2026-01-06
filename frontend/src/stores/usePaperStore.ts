/**
 * Paper store using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Paper, PaperFilters, PaperListResponse } from '@/types';
import { paperService } from '@/services';

interface PaperState {
  // State
  papers: Paper[];
  selectedPaper: Paper | null;
  total: number;
  page: number;
  pageSize: number;
  filters: PaperFilters;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchPapers: (page?: number, filters?: PaperFilters) => Promise<void>;
  fetchPaper: (id: string) => Promise<void>;
  setSelectedPaper: (paper: Paper | null) => void;
  setFilters: (filters: PaperFilters) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  reset: () => void;
}

const initialState = {
  papers: [],
  selectedPaper: null,
  total: 0,
  page: 1,
  pageSize: 20,
  filters: {},
  isLoading: false,
  error: null,
};

export const usePaperStore = create<PaperState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      fetchPapers: async (page?: number, filters?: PaperFilters) => {
        const currentPage = page ?? get().page;
        const currentFilters = filters ?? get().filters;

        set({ isLoading: true, error: null });

        try {
          const response: PaperListResponse = await paperService.list(
            currentPage,
            get().pageSize,
            currentFilters
          );

          set({
            papers: response.papers,
            total: response.total,
            page: response.page,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch papers',
            isLoading: false,
          });
        }
      },

      fetchPaper: async (id: string) => {
        set({ isLoading: true, error: null });

        try {
          const paper = await paperService.get(id);
          set({ selectedPaper: paper, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch paper',
            isLoading: false,
          });
        }
      },

      setSelectedPaper: (paper: Paper | null) => {
        set({ selectedPaper: paper });
      },

      setFilters: (filters: PaperFilters) => {
        set({ filters, page: 1 });
      },

      clearFilters: () => {
        set({ filters: {}, page: 1 });
      },

      setPage: (page: number) => {
        set({ page });
      },

      setPageSize: (pageSize: number) => {
        set({ pageSize, page: 1 });
      },

      reset: () => {
        set(initialState);
      },
    }),
    { name: 'paper-store' }
  )
);

export default usePaperStore;


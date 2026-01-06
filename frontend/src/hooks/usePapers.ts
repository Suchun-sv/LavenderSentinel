/**
 * React Query hooks for papers
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { paperService } from '@/services';
import type { PaperFilters, PaperCreate, PaperUpdate } from '@/types';

export const paperKeys = {
  all: ['papers'] as const,
  lists: () => [...paperKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, filters?: PaperFilters) =>
    [...paperKeys.lists(), page, pageSize, filters] as const,
  details: () => [...paperKeys.all, 'detail'] as const,
  detail: (id: string) => [...paperKeys.details(), id] as const,
};

export function usePapers(page = 1, pageSize = 20, filters?: PaperFilters) {
  return useQuery({
    queryKey: paperKeys.list(page, pageSize, filters),
    queryFn: () => paperService.list(page, pageSize, filters),
  });
}

export function usePaper(id: string) {
  return useQuery({
    queryKey: paperKeys.detail(id),
    queryFn: () => paperService.get(id),
    enabled: !!id,
  });
}

export function useCreatePaper() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paper: PaperCreate) => paperService.create(paper),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: paperKeys.lists() });
    },
  });
}

export function useUpdatePaper() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, paper }: { id: string; paper: PaperUpdate }) =>
      paperService.update(id, paper),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: paperKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: paperKeys.lists() });
    },
  });
}

export function useDeletePaper() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => paperService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: paperKeys.lists() });
    },
  });
}

export function useGenerateSummary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => paperService.generateSummary(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: paperKeys.detail(id) });
    },
  });
}


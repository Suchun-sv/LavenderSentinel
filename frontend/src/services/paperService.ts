/**
 * Paper API service
 */

import apiClient from './api';
import type {
  Paper,
  PaperCreate,
  PaperUpdate,
  PaperListResponse,
  PaperFilters,
  PaperSummary,
} from '@/types';

export const paperService = {
  /**
   * Get paginated list of papers
   */
  async list(
    page: number = 1,
    pageSize: number = 20,
    filters?: PaperFilters
  ): Promise<PaperListResponse> {
    const params: Record<string, unknown> = {
      page,
      page_size: pageSize,
      ...filters,
    };
    
    const response = await apiClient.get<PaperListResponse>('/papers', { params });
    return response.data;
  },

  /**
   * Get a single paper by ID
   */
  async get(paperId: string): Promise<Paper> {
    const response = await apiClient.get<Paper>(`/papers/${paperId}`);
    return response.data;
  },

  /**
   * Create a new paper
   */
  async create(paper: PaperCreate): Promise<Paper> {
    const response = await apiClient.post<Paper>('/papers', paper);
    return response.data;
  },

  /**
   * Update a paper
   */
  async update(paperId: string, paper: PaperUpdate): Promise<Paper> {
    const response = await apiClient.patch<Paper>(`/papers/${paperId}`, paper);
    return response.data;
  },

  /**
   * Delete a paper
   */
  async delete(paperId: string): Promise<void> {
    await apiClient.delete(`/papers/${paperId}`);
  },

  /**
   * Generate AI summary for a paper
   */
  async generateSummary(paperId: string): Promise<PaperSummary> {
    const response = await apiClient.post<PaperSummary>(`/papers/${paperId}/summarize`);
    return response.data;
  },

  /**
   * Get paper statistics
   */
  async getStats(): Promise<{
    total_papers: number;
    papers_with_summary: number;
    sources: Record<string, number>;
  }> {
    const response = await apiClient.get('/papers/stats');
    return response.data;
  },
};

export default paperService;


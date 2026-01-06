/**
 * Search API service
 */

import apiClient from './api';
import type {
  SearchRequest,
  SearchResponse,
  SimilarPapersRequest,
  SimilarPapersResponse,
  SearchSuggestion,
} from '@/types';

export const searchService = {
  /**
   * Perform semantic search on papers
   */
  async semanticSearch(request: SearchRequest): Promise<SearchResponse> {
    const response = await apiClient.post<SearchResponse>('/search/semantic', request);
    return response.data;
  },

  /**
   * Perform keyword search on papers
   */
  async keywordSearch(
    query: string,
    topK: number = 10,
    source?: string
  ): Promise<SearchResponse> {
    const params: Record<string, unknown> = {
      q: query,
      top_k: topK,
    };
    
    if (source) {
      params.source = source;
    }
    
    const response = await apiClient.get<SearchResponse>('/search/keyword', { params });
    return response.data;
  },

  /**
   * Find similar papers
   */
  async findSimilar(request: SimilarPapersRequest): Promise<SimilarPapersResponse> {
    const response = await apiClient.post<SimilarPapersResponse>('/search/similar', request);
    return response.data;
  },

  /**
   * Get search suggestions
   */
  async getSuggestions(query: string, limit: number = 5): Promise<SearchSuggestion[]> {
    const response = await apiClient.get<{ suggestions: SearchSuggestion[] }>(
      '/search/suggestions',
      {
        params: { q: query, limit },
      }
    );
    return response.data.suggestions;
  },
};

export default searchService;


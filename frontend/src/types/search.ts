/**
 * Search-related TypeScript types
 */

import type { Paper, PaperWithSimilarity } from './paper';

export interface SearchFilters {
  categories?: string[];
  keywords?: string[];
  sources?: string[];
  date_from?: string;
  date_to?: string;
  authors?: string[];
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  filters?: SearchFilters;
  include_summary?: boolean;
}

export interface SearchResult {
  paper: PaperWithSimilarity;
  highlights: string[];
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  took_ms: number;
}

export interface SimilarPapersRequest {
  paper_id: string;
  top_k?: number;
  exclude_same_authors?: boolean;
}

export interface SimilarPapersResponse {
  source_paper: Paper;
  similar_papers: PaperWithSimilarity[];
  total: number;
}

export interface SearchSuggestion {
  text: string;
  type: 'keyword' | 'author' | 'category';
}


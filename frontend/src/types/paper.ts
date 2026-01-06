/**
 * Paper-related TypeScript types
 */

export interface Author {
  name: string;
  affiliation?: string;
  email?: string;
}

export interface Paper {
  id: string;
  external_id: string;
  title: string;
  abstract: string;
  authors: Author[];
  keywords: string[];
  categories: string[];
  source: string;
  url: string;
  pdf_url?: string;
  published_at: string;
  collected_at: string;
  updated_at: string;
  summary?: string;
  key_points: string[];
}

export interface PaperWithSimilarity extends Paper {
  similarity_score: number;
}

export interface PaperCreate {
  external_id: string;
  title: string;
  abstract: string;
  authors: Author[];
  keywords: string[];
  categories: string[];
  source: string;
  url: string;
  pdf_url?: string;
  published_at: string;
}

export interface PaperUpdate {
  title?: string;
  abstract?: string;
  keywords?: string[];
  categories?: string[];
  pdf_url?: string;
}

export interface PaperSummary {
  paper_id: string;
  summary: string;
  key_points: string[];
  methodology?: string;
  findings?: string;
  limitations?: string;
  generated_at: string;
  model_used: string;
}

export interface PaperListResponse {
  papers: Paper[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaperFilters {
  source?: string;
  categories?: string[];
  date_from?: string;
  date_to?: string;
  keywords?: string[];
}


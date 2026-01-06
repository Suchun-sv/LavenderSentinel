/**
 * Search page component
 */

import { useState, type FormEvent } from 'react';
import { Search, SlidersHorizontal, Clock, X } from 'lucide-react';
import { Button, Input, Card, Badge } from '@/components/ui';
import { PaperList } from '@/components/paper';
import { useSearchStore } from '@/stores';
import { cn } from '@/lib/utils';

export function SearchPage() {
  const {
    query,
    results,
    total,
    tookMs,
    isLoading,
    recentSearches,
    search,
    setQuery,
    clearResults,
    clearRecentSearches,
  } = useSearchStore();

  const [showFilters, setShowFilters] = useState(false);
  const [localQuery, setLocalQuery] = useState(query);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (localQuery.trim()) {
      search(localQuery);
    }
  };

  const handleRecentClick = (recentQuery: string) => {
    setLocalQuery(recentQuery);
    search(recentQuery);
  };

  const papers = results.map((r) => r.paper);

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="space-y-4">
        <h1 className="text-2xl font-display font-bold">Search Papers</h1>

        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1">
            <Input
              type="search"
              placeholder="Search by topic, title, or keywords..."
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              leftIcon={<Search className="h-5 w-5" />}
              className="text-lg py-3"
            />
          </div>
          <Button type="submit" isLoading={isLoading} className="px-6">
            Search
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => setShowFilters(!showFilters)}
          >
            <SlidersHorizontal className="h-5 w-5" />
          </Button>
        </form>

        {/* Filters */}
        {showFilters && (
          <Card className="animate-in">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Source</label>
                <select className="input">
                  <option value="">All sources</option>
                  <option value="arxiv">arXiv</option>
                  <option value="semantic_scholar">Semantic Scholar</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <Input placeholder="e.g., cs.CL, cs.LG" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Date Range</label>
                <Input type="date" />
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Recent Searches */}
      {recentSearches.length > 0 && !results.length && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Recent Searches
            </h3>
            <button
              onClick={clearRecentSearches}
              className="text-xs text-[rgb(var(--muted-foreground))] hover:text-[rgb(var(--foreground))]"
            >
              Clear all
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((recentQuery, index) => (
              <button
                key={index}
                onClick={() => handleRecentClick(recentQuery)}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm
                         bg-[rgb(var(--muted))] hover:bg-lavender-100 dark:hover:bg-lavender-900/30
                         transition-colors"
              >
                {recentQuery}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[rgb(var(--muted-foreground))]">
              Found <span className="font-medium text-[rgb(var(--foreground))]">{total}</span> papers
              in {tookMs.toFixed(0)}ms
            </p>
            <Button variant="ghost" size="sm" onClick={clearResults}>
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>
          </div>

          <PaperList
            papers={papers}
            isLoading={isLoading}
            showScore={true}
          />
        </div>
      )}

      {/* Empty State */}
      {!results.length && !isLoading && query && (
        <div className="text-center py-12">
          <Search className="h-12 w-12 mx-auto text-[rgb(var(--muted-foreground))] mb-4" />
          <h3 className="font-semibold mb-2">No results found</h3>
          <p className="text-[rgb(var(--muted-foreground))]">
            Try different keywords or adjust your filters
          </p>
        </div>
      )}

      {/* Initial State */}
      {!results.length && !isLoading && !query && recentSearches.length === 0 && (
        <div className="text-center py-12">
          <Search className="h-12 w-12 mx-auto text-lavender-400 mb-4" />
          <h3 className="font-semibold mb-2">Search Academic Papers</h3>
          <p className="text-[rgb(var(--muted-foreground))] max-w-md mx-auto">
            Use natural language to find papers. Try queries like
            "transformer attention mechanisms" or "climate change machine learning"
          </p>
        </div>
      )}
    </div>
  );
}

export default SearchPage;


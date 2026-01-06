/**
 * Papers list page component
 */

import { useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button, Card } from '@/components/ui';
import { PaperList } from '@/components/paper';
import { usePaperStore } from '@/stores';

export function PapersPage() {
  const {
    papers,
    total,
    page,
    pageSize,
    isLoading,
    fetchPapers,
    setPage,
  } = usePaperStore();

  useEffect(() => {
    fetchPapers();
  }, [page, fetchPapers]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold">Papers</h1>
          <p className="text-[rgb(var(--muted-foreground))]">
            {total} papers in your collection
          </p>
        </div>
      </div>

      {/* Papers List */}
      <PaperList
        papers={papers}
        isLoading={isLoading}
        emptyMessage="No papers in your collection yet"
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          <div className="flex items-center gap-1">
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors
                    ${page === pageNum
                      ? 'bg-lavender-600 text-white'
                      : 'hover:bg-[rgb(var(--muted))]'
                    }`}
                >
                  {pageNum}
                </button>
              );
            })}
            {totalPages > 5 && (
              <>
                <span className="px-2">...</span>
                <button
                  onClick={() => setPage(totalPages)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors
                    ${page === totalPages
                      ? 'bg-lavender-600 text-white'
                      : 'hover:bg-[rgb(var(--muted))]'
                    }`}
                >
                  {totalPages}
                </button>
              </>
            )}
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}

export default PapersPage;


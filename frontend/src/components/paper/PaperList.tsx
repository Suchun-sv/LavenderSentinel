/**
 * Paper list component
 */

import { FileText } from 'lucide-react';
import { PaperCard } from './PaperCard';
import type { Paper, PaperWithSimilarity } from '@/types';

interface PaperListProps {
  papers: (Paper | PaperWithSimilarity)[];
  isLoading?: boolean;
  showScore?: boolean;
  emptyMessage?: string;
}

export function PaperList({
  papers,
  isLoading = false,
  showScore = false,
  emptyMessage = 'No papers found',
}: PaperListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="rounded-xl border border-[rgb(var(--border))] p-6 animate-pulse"
          >
            <div className="h-5 bg-[rgb(var(--muted))] rounded w-3/4 mb-3" />
            <div className="h-4 bg-[rgb(var(--muted))] rounded w-full mb-2" />
            <div className="h-4 bg-[rgb(var(--muted))] rounded w-5/6 mb-4" />
            <div className="flex gap-2">
              <div className="h-5 bg-[rgb(var(--muted))] rounded-full w-16" />
              <div className="h-5 bg-[rgb(var(--muted))] rounded-full w-16" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 mx-auto text-[rgb(var(--muted-foreground))] mb-4" />
        <p className="text-[rgb(var(--muted-foreground))]">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {papers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} showScore={showScore} />
      ))}
    </div>
  );
}

export default PaperList;


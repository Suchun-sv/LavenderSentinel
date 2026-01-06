/**
 * Paper card component
 */

import { Link } from 'react-router-dom';
import { Calendar, ExternalLink, FileText, Plus } from 'lucide-react';
import { Card, Badge, Button } from '@/components/ui';
import { formatDate, truncate } from '@/lib/utils';
import { useChatStore } from '@/stores';
import type { Paper, PaperWithSimilarity } from '@/types';

interface PaperCardProps {
  paper: Paper | PaperWithSimilarity;
  showScore?: boolean;
}

export function PaperCard({ paper, showScore = false }: PaperCardProps) {
  const { addToPaperContext, paperContext } = useChatStore();
  const isInContext = paperContext.includes(paper.id);
  const score = 'similarity_score' in paper ? paper.similarity_score : undefined;

  return (
    <Card hover className="group">
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1 min-w-0">
          <Link
            to={`/papers/${paper.id}`}
            className="block group-hover:text-lavender-600 transition-colors"
          >
            <h3 className="font-semibold text-base mb-2 line-clamp-2">
              {paper.title}
            </h3>
          </Link>

          <p className="text-sm text-[rgb(var(--muted-foreground))] mb-3 line-clamp-3">
            {truncate(paper.abstract, 200)}
          </p>

          {/* Authors */}
          <p className="text-xs text-[rgb(var(--muted-foreground))] mb-3">
            {paper.authors.slice(0, 3).map((a) => a.name).join(', ')}
            {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
          </p>

          {/* Categories */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {paper.categories.slice(0, 3).map((category) => (
              <Badge key={category} variant="secondary" size="sm">
                {category}
              </Badge>
            ))}
            {paper.categories.length > 3 && (
              <Badge variant="secondary" size="sm">
                +{paper.categories.length - 3}
              </Badge>
            )}
          </div>

          {/* Meta */}
          <div className="flex items-center gap-4 text-xs text-[rgb(var(--muted-foreground))]">
            <span className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              {formatDate(paper.published_at)}
            </span>
            <Badge variant="primary" size="sm">
              {paper.source}
            </Badge>
            {showScore && score !== undefined && (
              <span className="text-lavender-600 font-medium">
                {(score * 100).toFixed(1)}% match
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => addToPaperContext(paper.id)}
            disabled={isInContext}
            title={isInContext ? 'Already in chat context' : 'Add to chat context'}
          >
            <Plus className={`h-4 w-4 ${isInContext ? 'text-lavender-500' : ''}`} />
          </Button>
          {paper.pdf_url && (
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg hover:bg-[rgb(var(--muted))] transition-colors"
              title="View PDF"
            >
              <FileText className="h-4 w-4" />
            </a>
          )}
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-lg hover:bg-[rgb(var(--muted))] transition-colors"
            title="View source"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </Card>
  );
}

export default PaperCard;


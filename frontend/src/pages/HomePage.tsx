/**
 * Home page component
 */

import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Search, Sparkles, TrendingUp } from 'lucide-react';
import { Button, Card, CardContent, CardTitle } from '@/components/ui';
import { PaperList } from '@/components/paper';
import { usePaperStore } from '@/stores';

export function HomePage() {
  const { papers, isLoading, fetchPapers } = usePaperStore();

  useEffect(() => {
    fetchPapers(1);
  }, [fetchPapers]);

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-lavender-500 to-lavender-700 p-8 md:p-12">
        <div className="relative z-10">
          <h1 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">
            Your Reliable Sentinel for
            <br />
            <span className="text-lavender-200">Academic Literature</span>
          </h1>
          <p className="text-lavender-100 text-lg mb-6 max-w-xl">
            Automatically collect, index, and summarize research papers.
            Deep dive into any topic with AI-powered conversation.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/search">
              <Button className="bg-white text-lavender-700 hover:bg-lavender-50">
                <Search className="h-4 w-4" />
                Start Searching
              </Button>
            </Link>
            <Link to="/chat">
              <Button variant="ghost" className="text-white hover:bg-white/20">
                <Sparkles className="h-4 w-4" />
                Chat with AI
              </Button>
            </Link>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-lavender-400/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-lavender-600/30 rounded-full blur-3xl" />
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Papers Indexed', value: papers.length, icon: BookOpen },
          { label: 'Topics Tracked', value: 12, icon: TrendingUp },
          { label: 'AI Summaries', value: 0, icon: Sparkles },
          { label: 'Searches Today', value: 45, icon: Search },
        ].map((stat) => (
          <Card key={stat.label} className="text-center">
            <CardContent>
              <stat.icon className="h-6 w-6 mx-auto mb-2 text-lavender-500" />
              <div className="text-2xl font-bold font-display">{stat.value}</div>
              <div className="text-sm text-[rgb(var(--muted-foreground))]">
                {stat.label}
              </div>
            </CardContent>
          </Card>
        ))}
      </section>

      {/* Recent Papers */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <CardTitle>Recent Papers</CardTitle>
          <Link to="/papers" className="text-sm text-lavender-600 hover:underline flex items-center gap-1">
            View all
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <PaperList
          papers={papers.slice(0, 5)}
          isLoading={isLoading}
          emptyMessage="No papers collected yet. Add some keywords to start tracking!"
        />
      </section>
    </div>
  );
}

export default HomePage;


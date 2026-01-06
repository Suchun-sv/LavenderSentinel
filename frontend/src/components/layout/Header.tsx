/**
 * Header component
 */

import { Link } from 'react-router-dom';
import { Search, Settings, Menu } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { useSearchStore } from '@/stores';
import { useState, type FormEvent } from 'react';

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { search } = useSearchStore();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      search(searchQuery);
    }
  };

  return (
    <header className="sticky top-0 z-50 glass border-b border-[rgb(var(--border))]">
      <div className="flex items-center justify-between px-4 py-3 lg:px-6">
        {/* Left section */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-lavender-400 to-lavender-600 flex items-center justify-center">
              <span className="text-white font-display font-bold text-lg">L</span>
            </div>
            <span className="hidden sm:block font-display font-semibold text-lg gradient-text">
              LavenderSentinel
            </span>
          </Link>
        </div>

        {/* Center - Search */}
        <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-4">
          <Input
            type="search"
            placeholder="Search papers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="h-4 w-4" />}
            className="bg-[rgb(var(--muted))]/50"
          />
        </form>

        {/* Right section */}
        <div className="flex items-center gap-2">
          <Link to="/settings">
            <Button variant="ghost" size="sm">
              <Settings className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default Header;


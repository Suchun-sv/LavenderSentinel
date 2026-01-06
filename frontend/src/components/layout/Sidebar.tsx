/**
 * Sidebar component
 */

import { NavLink } from 'react-router-dom';
import { Home, Search, FileText, MessageSquare, Bookmark, TrendingUp, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Papers', href: '/papers', icon: FileText },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Saved', href: '/saved', icon: Bookmark },
  { name: 'Trending', href: '/trending', icon: TrendingUp },
];

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-[rgb(var(--card))] border-r border-[rgb(var(--border))]',
          'transform transition-transform duration-300 ease-in-out',
          'lg:relative lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Close button (mobile) */}
          <div className="flex justify-end p-4 lg:hidden">
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                    'transition-colors duration-200',
                    isActive
                      ? 'bg-lavender-100 text-lavender-700 dark:bg-lavender-900/30 dark:text-lavender-300'
                      : 'text-[rgb(var(--muted-foreground))] hover:bg-[rgb(var(--muted))] hover:text-[rgb(var(--foreground))]'
                  )
                }
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* Bottom section */}
          <div className="p-4 border-t border-[rgb(var(--border))]">
            <div className="p-4 rounded-lg bg-gradient-to-br from-lavender-500/10 to-lavender-600/10">
              <h4 className="font-medium text-sm mb-1">Pro Tip</h4>
              <p className="text-xs text-[rgb(var(--muted-foreground))]">
                Use the chat panel to ask questions about any paper in your collection.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;


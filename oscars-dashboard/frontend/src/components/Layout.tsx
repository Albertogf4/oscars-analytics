import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
  timestamp?: string;
}

export function Layout({ children, timestamp }: LayoutProps) {
  const location = useLocation();
  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short',
      })
    : null;

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="group cursor-pointer">
              <h1 className="text-2xl font-semibold tracking-tight text-text-primary text-hover-underline inline-block">
                Oscar Markets
              </h1>
              <p className="text-sm text-text-secondary mt-1 group-hover:text-text-primary transition-colors">
                Live prediction market data
              </p>
            </Link>
            <nav className="flex gap-4">
              <Link
                to="/"
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/'
                    ? 'bg-bg-secondary text-accent-gold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                }`}
              >
                Markets
              </Link>
              <Link
                to="/memes"
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/memes'
                    ? 'bg-bg-secondary text-accent-gold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                }`}
              >
                Meme Studio
              </Link>
              <Link
                to="/templates"
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/templates'
                    ? 'bg-bg-secondary text-accent-gold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                }`}
              >
                Templates
              </Link>
            </nav>
          </div>
          {formattedTime && (
            <div className="text-right px-3 py-2 rounded transition-colors hover:bg-bg-secondary">
              <p className="text-xs text-text-muted uppercase tracking-wide">
                Last Updated
              </p>
              <p className="text-sm text-text-secondary font-mono">
                {formattedTime}
              </p>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-10">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-xs text-text-muted text-center hover:text-text-secondary transition-colors cursor-default">
            Data from <span className="hover:text-accent-gold transition-colors">Kalshi</span> prediction markets
          </p>
        </div>
      </footer>
    </div>
  );
}

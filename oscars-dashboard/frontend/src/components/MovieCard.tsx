import { motion } from 'framer-motion';
import type { MovieComparison } from '../types/markets';

interface MovieCardProps {
  movie: MovieComparison;
  rank: number;
  isLeader?: boolean;
}

function formatVolume(volume: number): string {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(1)}M`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(0)}K`;
  }
  return volume.toString();
}

export function MovieCard({ movie, rank, isLeader }: MovieCardProps) {
  const bestPictureOdds = movie.best_picture_odds ?? 0;
  const isHighOdds = bestPictureOdds >= 50;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.1 }}
      whileHover={{
        y: -6,
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
      className={`card card-interactive ${isLeader ? 'glow-gold ring-1 ring-accent-gold/30' : ''}`}
    >
      {/* Rank indicator */}
      <div className="flex items-start justify-between mb-6">
        <span className="text-sm font-mono text-text-muted px-2 py-0.5 rounded bg-bg-secondary/50 transition-colors hover:bg-border hover:text-text-primary">
          #{rank}
        </span>
        {isLeader && (
          <motion.span
            className="leader-badge"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            Frontrunner
          </motion.span>
        )}
      </div>

      {/* Movie Title */}
      <h2 className="text-2xl font-semibold tracking-tight text-text-primary mb-1">
        {movie.name}
      </h2>
      <p className="text-sm text-text-secondary mb-8">
        Directed by {movie.director}
      </p>

      {/* Best Picture Odds - Hero Metric */}
      <div className="mb-8">
        <p className="text-xs text-text-muted uppercase tracking-wide mb-2">
          Best Picture
        </p>
        <motion.div
          className="flex items-baseline gap-1"
          whileHover={{ scale: 1.02, x: 2 }}
          transition={{ duration: 0.2 }}
        >
          <span className={`price-display ${isHighOdds ? 'text-accent-green price-pulse' : 'text-text-primary'}`}>
            {bestPictureOdds}
          </span>
          <span className="text-xl text-text-secondary font-mono">%</span>
        </motion.div>
      </div>

      {/* Secondary Metrics Grid */}
      <div className="grid grid-cols-2 gap-2 pt-6 border-t border-border">
        <div className="metric-cell">
          <p className="text-xs text-text-muted uppercase tracking-wide mb-1">
            Avg Odds
          </p>
          <p className="text-lg font-mono text-text-primary">
            {movie.metrics.avg_yes_price.toFixed(1)}%
          </p>
        </div>
        <div className="metric-cell">
          <p className="text-xs text-text-muted uppercase tracking-wide mb-1">
            Volume
          </p>
          <p className="text-lg font-mono text-text-primary">
            ${formatVolume(movie.metrics.total_volume)}
          </p>
        </div>
        <div className="metric-cell">
          <p className="text-xs text-text-muted uppercase tracking-wide mb-1">
            Markets
          </p>
          <p className="text-lg font-mono text-text-primary">
            {movie.metrics.total_markets}
          </p>
        </div>
        <div className="metric-cell">
          <p className="text-xs text-text-muted uppercase tracking-wide mb-1">
            Open Interest
          </p>
          <p className="text-lg font-mono text-text-primary">
            ${formatVolume(movie.metrics.total_open_interest)}
          </p>
        </div>
      </div>

      {/* Categories */}
      <div className="mt-6 pt-4 border-t border-border/50">
        <p className="text-xs text-text-muted mb-2">Categories</p>
        <div className="flex flex-wrap gap-1.5">
          {movie.metrics.categories.slice(0, 5).map((cat) => (
            <span
              key={cat}
              className="px-2 py-0.5 text-xs text-text-secondary bg-bg-secondary rounded badge-interactive"
            >
              {cat}
            </span>
          ))}
          {movie.metrics.categories.length > 5 && (
            <span
              className="px-2 py-0.5 text-xs text-text-muted hover:text-text-secondary transition-colors cursor-default"
              title={movie.metrics.categories.slice(5).join(', ')}
            >
              +{movie.metrics.categories.length - 5} more
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

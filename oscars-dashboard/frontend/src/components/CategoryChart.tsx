import { motion } from 'framer-motion';
import type { HeadToHead } from '../types/markets';

interface CategoryChartProps {
  data: HeadToHead;
  movieColors: Record<string, string>;
}

export function CategoryChart({ data, movieColors }: CategoryChartProps) {
  const entries = Object.entries(data.markets).sort(
    ([, a], [, b]) => b.price - a.price
  );
  const maxPrice = Math.max(...entries.map(([, m]) => m.price), 1);

  return (
    <div className="mb-6 last:mb-0">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-text-primary hover:text-accent-gold transition-colors cursor-default">
          {data.category}
        </h4>
        <span className="text-xs text-text-muted px-2 py-0.5 rounded hover:bg-bg-secondary hover:text-accent-green transition-all">
          Leader: {data.leader?.split(' ')[0] || 'TBD'}
        </span>
      </div>

      <div className="space-y-2">
        {entries.map(([movieName, market], idx) => {
          const widthPercent = (market.price / maxPrice) * 100;
          const isLeader = movieName === data.leader;
          const color = movieColors[movieName] || '#404040';

          return (
            <div key={movieName} className="flex items-center gap-3 group">
              <span className="w-20 text-xs text-text-secondary truncate group-hover:text-text-primary transition-colors">
                {movieName.split(' ')[0]}
              </span>
              <div className="flex-1 h-6 bg-bg-secondary rounded overflow-hidden tooltip-container">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${widthPercent}%` }}
                  transition={{ delay: 0.5 + idx * 0.1, duration: 0.5 }}
                  whileHover={{
                    filter: 'brightness(1.2)',
                    transition: { duration: 0.15 }
                  }}
                  className="h-full rounded flex items-center justify-end pr-2 cursor-pointer chart-bar"
                  style={{ backgroundColor: color }}
                >
                  <span
                    className={`text-xs font-mono ${
                      isLeader ? 'text-white font-medium' : 'text-white/80'
                    }`}
                  >
                    {market.price}%
                  </span>
                </motion.div>
                <div className="tooltip">
                  <div className="font-medium">{movieName}</div>
                  <div className="text-text-secondary">Odds: {market.price}%</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface CategoryChartsProps {
  headToHead: HeadToHead[];
}

export function CategoryCharts({ headToHead }: CategoryChartsProps) {
  const movieColors: Record<string, string> = {
    'One Battle After Another': '#d4af37', // Gold
    'Sinners': '#6366f1', // Indigo
    'Hamnet': '#8b5cf6', // Purple
  };

  // Show top categories only
  const topCategories = ['Best Picture', 'Best Director', 'Best Actor', 'Best Actress'];
  const filtered = headToHead.filter((h) => topCategories.includes(h.category));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.4 }}
      className="card"
    >
      <h3 className="text-lg font-semibold text-text-primary mb-6">
        Key Categories
      </h3>

      {filtered.map((data) => (
        <CategoryChart key={data.category} data={data} movieColors={movieColors} />
      ))}

      {/* Legend */}
      <div className="flex items-center gap-4 mt-6 pt-4 border-t border-border/50">
        {Object.entries(movieColors).map(([name, color]) => (
          <motion.div
            key={name}
            className="flex items-center gap-2 legend-item px-2 py-1 rounded"
            whileHover={{
              scale: 1.05,
              backgroundColor: 'rgba(38, 38, 38, 0.5)'
            }}
            transition={{ duration: 0.15 }}
          >
            <div
              className="w-3 h-3 rounded-sm transition-transform group-hover:scale-110"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-text-secondary">{name.split(' ')[0]}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

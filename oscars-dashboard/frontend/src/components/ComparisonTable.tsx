import { motion } from 'framer-motion';
import type { HeadToHead, MovieComparison } from '../types/markets';

interface ComparisonTableProps {
  headToHead: HeadToHead[];
  movies: MovieComparison[];
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

export function ComparisonTable({ headToHead, movies }: ComparisonTableProps) {
  const movieNames = movies.map((m) => m.name);

  // Filter to show only main categories
  const mainCategories = [
    'Best Picture',
    'Best Director',
    'Best Actor',
    'Best Actress',
    'Supporting Actor',
    'Supporting Actress',
    'Original Screenplay',
    'Adapted Screenplay',
    'Cinematography',
    'Original Score',
    'Film Editing',
  ];

  const filteredH2H = headToHead.filter((h) =>
    mainCategories.includes(h.category)
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3 }}
      className="card overflow-hidden"
    >
      <h3 className="text-lg font-semibold text-text-primary mb-6">
        Head-to-Head by Category
      </h3>

      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th className="w-48">Category</th>
              {movieNames.map((name) => (
                <th key={name} className="text-center min-w-[140px]">
                  <span className="text-text-primary hover:text-accent-gold transition-colors cursor-default">
                    {name.split(' ')[0]}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredH2H.map((row, idx) => (
              <motion.tr
                key={row.category}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + idx * 0.05 }}
                className="table-row-interactive"
                whileHover={{
                  backgroundColor: 'rgba(38, 38, 38, 0.3)'
                }}
              >
                <td className="font-medium text-text-primary hover:text-accent-gold transition-colors cursor-default">
                  {row.category}
                </td>
                {movieNames.map((name) => {
                  const market = row.markets[name];
                  const isLeader = row.leader === name;
                  const price = market?.price ?? 0;

                  return (
                    <td key={name} className="text-center">
                      {market ? (
                        <motion.div
                          className="flex flex-col items-center py-1 px-2 rounded cursor-default"
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: 'rgba(38, 38, 38, 0.4)'
                          }}
                          transition={{ duration: 0.15 }}
                        >
                          <span
                            className={`font-mono text-lg ${
                              isLeader
                                ? 'text-accent-green font-semibold'
                                : 'text-text-primary'
                            }`}
                          >
                            {price}%
                          </span>
                          <span className="text-xs text-text-muted mt-0.5">
                            ${formatVolume(market.volume)}
                          </span>
                        </motion.div>
                      ) : (
                        <span className="text-text-muted">—</span>
                      )}
                    </td>
                  );
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredH2H.length === 0 && (
        <div className="py-8 text-center text-text-muted">
          No head-to-head data available
        </div>
      )}
    </motion.div>
  );
}

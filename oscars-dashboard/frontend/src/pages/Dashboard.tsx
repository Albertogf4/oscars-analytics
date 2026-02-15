import { useMarkets } from '../hooks/useMarkets';
import { Layout } from '../components/Layout';
import { MovieCard } from '../components/MovieCard';
import { ComparisonTable } from '../components/ComparisonTable';
import { CategoryCharts } from '../components/CategoryChart';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

function LoadingState() {
  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-2 border-text-muted border-t-accent-gold rounded-full animate-spin mb-4" />
          <p className="text-text-secondary">Loading market data...</p>
        </div>
      </div>
    </Layout>
  );
}

function ErrorState({ error }: { error: Error }) {
  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center card max-w-md">
          <div className="text-accent-red text-4xl mb-4">!</div>
          <h2 className="text-xl font-semibold text-text-primary mb-2">
            Failed to load data
          </h2>
          <p className="text-text-secondary text-sm mb-4">
            {error.message}
          </p>
          <p className="text-text-muted text-xs">
            Make sure the backend server is running on port 8000
          </p>
        </div>
      </div>
    </Layout>
  );
}

export function Dashboard() {
  const { data, isLoading, error } = useMarkets();

  if (isLoading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState error={error as Error} />;
  }

  if (!data) {
    return <LoadingState />;
  }

  const { movies, head_to_head, timestamp } = data;

  return (
    <Layout timestamp={timestamp}>
      {/* Hero Section - Summary Stats */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12"
      >
        <div className="flex items-baseline gap-4 mb-2">
          <h2 className="text-4xl font-semibold tracking-tight text-text-primary">
            Oscar Race 2025
          </h2>
          <span className="text-sm text-text-muted">
            {data.summary.total_markets_scanned} markets analyzed
          </span>
        </div>
        <p className="text-text-secondary max-w-2xl">
          Real-time prediction market odds for this year's top Oscar contenders.
          Prices represent the market's implied probability of winning.
        </p>
      </motion.div>

      {/* Movie Cards Grid */}
      <section className="mb-16">
        <h3 className="text-sm font-medium text-text-muted uppercase tracking-wide mb-6 hover:text-text-secondary transition-colors cursor-default">
          Top Contenders
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {movies.map((movie, idx) => (
            <MovieCard
              key={movie.name}
              movie={movie}
              rank={idx + 1}
              isLeader={idx === 0}
            />
          ))}
        </div>
      </section>

      {/* Charts + Table Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-16">
        {/* Category Charts */}
        <CategoryCharts headToHead={head_to_head} />

        {/* Comparison Table */}
        <ComparisonTable headToHead={head_to_head} movies={movies} />
      </div>

      {/* All Markets Section */}
      <section>
        <h3 className="text-sm font-medium text-text-muted uppercase tracking-wide mb-6 hover:text-text-secondary transition-colors cursor-default">
          All Markets by Movie
        </h3>

        <div className="space-y-8">
          {movies.map((movie) => (
            <motion.div
              key={movie.name}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              whileHover={{ scale: 1.005 }}
              transition={{ duration: 0.2 }}
              className="card card-interactive"
            >
              <h4 className="text-lg font-semibold text-text-primary mb-4 hover:text-accent-gold transition-colors cursor-default">
                {movie.name}
              </h4>

              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Market</th>
                      <th className="text-right">Price</th>
                      <th className="text-right">Volume</th>
                      <th className="text-right">Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movie.markets
                      .sort((a, b) => (b.yes_price || 0) - (a.yes_price || 0))
                      .slice(0, 10)
                      .map((market) => (
                        <tr key={market.ticker} className="table-row-interactive cursor-default">
                          <td className="text-text-primary max-w-md">
                            <span className="block truncate" title={market.title}>{market.title}</span>
                            {market.subtitle && (
                              <span className="text-xs text-text-muted block truncate" title={market.subtitle}>
                                {market.subtitle}
                              </span>
                            )}
                          </td>
                          <td className="text-right font-mono text-text-primary">
                            <span className="hover:text-accent-green transition-colors">
                              {market.yes_price}%
                            </span>
                          </td>
                          <td className="text-right font-mono text-text-secondary">
                            ${(market.volume / 1000).toFixed(0)}K
                          </td>
                          <td className="text-right">
                            <span className="text-xs text-text-muted bg-bg-secondary px-2 py-0.5 rounded badge-interactive">
                              {market.category}
                            </span>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              {movie.markets.length > 10 && (
                <p className="text-xs text-text-muted mt-4 text-center">
                  Showing top 10 of {movie.markets.length} markets
                </p>
              )}
            </motion.div>
          ))}
        </div>
      </section>

      {/* Meme Campaign CTA */}
      <section className="mt-16">
        <Link to="/memes">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="card card-interactive p-8 text-center cursor-pointer border border-border hover:border-accent-gold/50 transition-colors"
          >
            <h3 className="text-2xl font-semibold text-text-primary mb-2">
              Meme Campaign
            </h3>
            <p className="text-text-secondary mb-4">
              Generate AI-powered memes from real sentiment data
            </p>
            <span className="inline-flex items-center gap-2 text-accent-gold font-medium">
              Go to Meme Studio
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </motion.div>
        </Link>
      </section>
    </Layout>
  );
}

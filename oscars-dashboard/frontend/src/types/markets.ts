export interface Market {
  ticker: string;
  title: string;
  subtitle?: string;
  category: string;
  yes_price: number;
  yes_bid?: number;
  no_price?: number;
  volume: number;
  volume_24h?: number;
  open_interest?: number;
  matched_keywords: string[];
}

export interface MovieMetrics {
  total_markets: number;
  avg_yes_price: number;
  total_volume: number;
  total_open_interest: number;
  categories: string[];
}

export interface MovieComparison {
  name: string;
  director: string;
  year: number;
  markets: Market[];
  metrics: MovieMetrics;
  best_picture_odds?: number;
  best_director_odds?: number;
  best_actor_odds?: number;
  best_actress_odds?: number;
}

export interface HeadToHeadMarket {
  price: number;
  volume: number;
  ticker: string;
}

export interface HeadToHead {
  category: string;
  leader: string;
  markets: Record<string, HeadToHeadMarket>;
}

export interface ComparisonResponse {
  timestamp: string;
  movies: MovieComparison[];
  head_to_head: HeadToHead[];
  summary: {
    total_markets_scanned: number;
    movies_analyzed: number;
  };
}

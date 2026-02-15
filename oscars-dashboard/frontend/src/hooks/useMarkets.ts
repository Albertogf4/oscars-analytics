import { useQuery } from '@tanstack/react-query';
import type { ComparisonResponse } from '../types/markets';

const API_BASE = 'http://localhost:8000';

async function fetchComparison(): Promise<ComparisonResponse> {
  const response = await fetch(`${API_BASE}/api/comparison`);
  if (!response.ok) {
    throw new Error('Failed to fetch market data');
  }
  return response.json();
}

export function useMarkets() {
  return useQuery({
    queryKey: ['markets', 'comparison'],
    queryFn: fetchComparison,
    refetchInterval: 60000, // Refresh every 60 seconds
    staleTime: 30000, // Consider data stale after 30 seconds
  });
}

export function useRefreshMarkets() {
  const refresh = async () => {
    const response = await fetch(`${API_BASE}/api/refresh`, { method: 'POST' });
    if (!response.ok) {
      throw new Error('Failed to refresh data');
    }
    return response.json();
  };

  return refresh;
}

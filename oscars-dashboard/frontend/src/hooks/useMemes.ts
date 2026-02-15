import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  MemeListResponse,
  TemplateListResponse,
  GenerateRequest,
  GenerateResponse,
} from '../types/memes';

const API_BASE = 'http://localhost:8000';

async function fetchMemes(category?: string): Promise<MemeListResponse> {
  const url = category
    ? `${API_BASE}/api/memes?category=${category}`
    : `${API_BASE}/api/memes`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch memes');
  }
  return response.json();
}

async function fetchTemplates(): Promise<TemplateListResponse> {
  const response = await fetch(`${API_BASE}/api/memes/templates`);
  if (!response.ok) {
    throw new Error('Failed to fetch templates');
  }
  return response.json();
}

async function generateMemes(request: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/api/memes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error('Failed to generate memes');
  }
  return response.json();
}

export function useMemes(category?: 'pro_obaa' | 'anti_sinners') {
  return useQuery({
    queryKey: ['memes', category],
    queryFn: () => fetchMemes(category),
    staleTime: 30000,
  });
}

export function useMemeTemplates() {
  return useQuery({
    queryKey: ['memes', 'templates'],
    queryFn: fetchTemplates,
    staleTime: 60000 * 5, // Templates don't change often
  });
}

export function useGenerateMemes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: generateMemes,
    onSuccess: () => {
      // Invalidate memes list to refetch with new memes
      queryClient.invalidateQueries({ queryKey: ['memes'] });
    },
  });
}

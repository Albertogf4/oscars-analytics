import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  TemplateInfoListResponse,
  ProcessingStatus,
  UploadResponse,
  FinalizeRequest,
  FinalizeResponse,
} from '../types/memes';

const API_BASE = 'http://localhost:8000';

// Fetch all templates
export function useTemplates() {
  return useQuery<TemplateInfoListResponse>({
    queryKey: ['templates'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/templates`);
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      return response.json();
    },
  });
}

// Upload a new template
export function useUploadTemplate() {
  const queryClient = useQueryClient();

  return useMutation<UploadResponse, Error, File>({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/api/templates/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

// Get processing status
export function useProcessingStatus(jobId: string | null, options?: { enabled?: boolean }) {
  return useQuery<ProcessingStatus>({
    queryKey: ['processing-status', jobId],
    queryFn: async () => {
      if (!jobId) {
        throw new Error('No job ID provided');
      }
      const response = await fetch(`${API_BASE}/api/templates/process/${jobId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch processing status');
      }
      return response.json();
    },
    enabled: !!jobId && (options?.enabled !== false),
    refetchInterval: (query) => {
      const data = query.state.data;
      // Keep polling if still running
      if (data?.status === 'pending' || data?.status === 'running') {
        return 1000; // Poll every second
      }
      return false; // Stop polling
    },
  });
}

// Finalize and integrate template
export function useFinalizeTemplate() {
  const queryClient = useQueryClient();

  return useMutation<FinalizeResponse, Error, FinalizeRequest>({
    mutationFn: async (request: FinalizeRequest) => {
      const response = await fetch(`${API_BASE}/api/templates/finalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to finalize template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

// Delete a template
export function useDeleteTemplate() {
  const queryClient = useQueryClient();

  return useMutation<{ message: string; manual_steps: string[] }, Error, string>({
    mutationFn: async (templateId: string) => {
      const response = await fetch(`${API_BASE}/api/templates/${templateId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

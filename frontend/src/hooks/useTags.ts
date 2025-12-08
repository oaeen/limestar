import { useState, useEffect, useCallback } from 'react';
import { tagsAPI } from '../services/api';
import type { TagWithCount } from '../types';

interface UseTagsResult {
  tags: TagWithCount[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useTags(): UseTagsResult {
  const [tags, setTags] = useState<TagWithCount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTags = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await tagsAPI.getAll();
      setTags(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch tags'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  return {
    tags,
    isLoading,
    error,
    refetch: fetchTags,
  };
}

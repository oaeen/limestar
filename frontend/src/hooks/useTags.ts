import { useState, useEffect, useCallback } from 'react';
import { tagsAPI } from '../services/api';
import type { TagWithCount, CategoryWithTags } from '../types';

interface UseTagsResult {
  tags: TagWithCount[];
  categories: CategoryWithTags[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useTags(): UseTagsResult {
  const [tags, setTags] = useState<TagWithCount[]>([]);
  const [categories, setCategories] = useState<CategoryWithTags[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTags = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [tagsResponse, categoriesResponse] = await Promise.all([
        tagsAPI.getAll(),
        tagsAPI.getCategories(),
      ]);
      setTags(tagsResponse);
      setCategories(categoriesResponse);
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
    categories,
    isLoading,
    error,
    refetch: fetchTags,
  };
}

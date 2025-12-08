import { useState, useEffect, useCallback, useRef } from 'react';
import { linksAPI, searchAPI } from '../services/api';
import type { Link, LinkListResponse } from '../types';

interface UseLinksParams {
  searchQuery?: string;
  selectedTags?: string[];
  page?: number;
  pageSize?: number;
}

interface UseLinksResult {
  links: Link[];
  total: number;
  hasMore: boolean;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  deleteLink: (id: number) => Promise<void>;
}

export function useLinks({
  searchQuery = '',
  selectedTags = [],
  page = 1,
  pageSize = 20,
}: UseLinksParams = {}): UseLinksResult {
  const [data, setData] = useState<LinkListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const isFirstLoad = useRef(true);

  const fetchLinks = useCallback(async () => {
    // 只在首次加载时显示 loading，避免搜索时卡片闪烁
    if (isFirstLoad.current) {
      setIsLoading(true);
    }
    setError(null);

    try {
      let response: LinkListResponse;

      if (searchQuery || selectedTags.length > 0) {
        // Use search API
        response = await searchAPI.search({
          q: searchQuery || undefined,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          page,
          page_size: pageSize,
        });
      } else {
        // Use links API
        response = await linksAPI.getAll({
          page,
          page_size: pageSize,
        });
      }

      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch links'));
    } finally {
      setIsLoading(false);
      isFirstLoad.current = false;
    }
  }, [searchQuery, selectedTags, page, pageSize]);

  useEffect(() => {
    fetchLinks();
  }, [fetchLinks]);

  const deleteLink = useCallback(async (id: number) => {
    try {
      await linksAPI.delete(id);
      // 乐观更新：立即从列表中移除
      setData((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((link) => link.id !== id),
              total: prev.total - 1,
            }
          : null
      );
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to delete link'));
      // 删除失败时重新获取列表
      fetchLinks();
    }
  }, [fetchLinks]);

  return {
    links: data?.items ?? [],
    total: data?.total ?? 0,
    hasMore: data?.has_more ?? false,
    isLoading,
    error,
    refetch: fetchLinks,
    deleteLink,
  };
}

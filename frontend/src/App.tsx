import { useState, useCallback, useMemo, useEffect } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { TagFilter } from './components/TagFilter';
import { LinkList } from './components/LinkList';
import { useLinks } from './hooks/useLinks';
import { useTags } from './hooks/useTags';

function App() {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Debounced search
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // 正确的防抖实现：使用 useEffect 确保定时器被正确清理
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
  }, []);

  // Fetch data
  const { tags, refetch: refetchTags } = useTags();
  const { links, isLoading, deleteLink } = useLinks({
    searchQuery: debouncedQuery,
    selectedTags,
  });

  // 删除链接
  const handleDeleteLink = useCallback(async (linkId: number) => {
    await deleteLink(linkId);
    refetchTags(); // 刷新标签计数
  }, [deleteLink, refetchTags]);

  // Tag selection handlers
  const handleTagSelect = useCallback((tagName: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagName)
        ? prev.filter((t) => t !== tagName)
        : [...prev, tagName]
    );
  }, []);

  const handleClearTags = useCallback(() => {
    setSelectedTags([]);
  }, []);

  // Filter tags that have links
  const visibleTags = useMemo(
    () => tags.filter((tag) => tag.count > 0),
    [tags]
  );

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        {/* Search */}
        <SearchBar
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="搜索标题、描述或备注..."
        />

        {/* Tags */}
        {visibleTags.length > 0 && (
          <TagFilter
            tags={visibleTags}
            selectedTags={selectedTags}
            onTagSelect={handleTagSelect}
            onClearAll={handleClearTags}
          />
        )}

        {/* Links */}
        <LinkList
          links={links}
          isLoading={isLoading}
          onTagClick={handleTagSelect}
          onDeleteLink={handleDeleteLink}
        />

        {/* Total count */}
        {!isLoading && links.length > 0 && (
          <p className="text-center text-sm text-gray-400 pt-4">
            共 {links.length} 条链接
          </p>
        )}
      </main>
    </div>
  );
}

export default App;

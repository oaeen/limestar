import { useState, useCallback, useEffect } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { TagFilter } from './components/TagFilter';
import { LinkList } from './components/LinkList';
import { AddLinkButton } from './components/AddLinkButton';
import { useLinks } from './hooks/useLinks';
import { useTags } from './hooks/useTags';
import { AuthProvider, useAuthContext } from './contexts/AuthContext';

function AppContent() {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Auth context
  const { isAuthenticated } = useAuthContext();

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
  const { categories, refetch: refetchTags } = useTags();
  const { links, isLoading, deleteLink, refetch } = useLinks({
    searchQuery: debouncedQuery,
    selectedTags,
  });

  // 删除链接（仅认证后可用）
  const handleDeleteLink = useCallback(async (linkId: number) => {
    await deleteLink(linkId);
    refetchTags(); // 刷新标签计数
  }, [deleteLink, refetchTags]);

  // 添加链接后的回调
  const handleLinkAdded = useCallback(() => {
    refetch();      // 刷新链接列表
    refetchTags();  // 刷新标签
  }, [refetch, refetchTags]);

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
        {categories.length > 0 && (
          <TagFilter
            categories={categories}
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
          onDeleteLink={isAuthenticated ? handleDeleteLink : undefined}
        />

        {/* Total count */}
        {!isLoading && links.length > 0 && (
          <p className="text-center text-sm text-gray-400 pt-4">
            共 {links.length} 条链接
          </p>
        )}
      </main>

      {/* 添加收藏按钮（仅认证后显示） */}
      <AddLinkButton onLinkAdded={handleLinkAdded} />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

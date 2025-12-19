import { motion } from 'framer-motion';
import type { CategoryWithTags } from '../types';

interface TagFilterProps {
  categories: CategoryWithTags[];
  selectedTags: string[];
  onTagSelect: (tagName: string) => void;
  onClearAll?: () => void;
}

export function TagFilter({
  categories,
  selectedTags,
  onTagSelect,
  onClearAll,
}: TagFilterProps) {
  // Filter categories with links
  const visibleCategories = categories.filter((c) => c.count > 0);

  return (
    <div className="space-y-4">
      {/* "All" button */}
      <motion.button
        className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
          selectedTags.length === 0
            ? 'bg-gray-900 text-white'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
        }`}
        onClick={onClearAll}
        whileTap={{ scale: 0.97 }}
      >
        全部
      </motion.button>

      {/* Categories with tags */}
      {visibleCategories.map((category) => (
        <div key={category.id} className="flex flex-wrap items-center gap-2">
          {/* Category label */}
          <span
            className="px-3 py-1.5 rounded-lg text-sm font-medium text-white"
            style={{ backgroundColor: category.color }}
          >
            {category.name}
          </span>

          {/* Child tags */}
          {category.tags
            .filter((tag) => tag.count > 0)
            .map((tag) => {
              const isActive = selectedTags.includes(tag.name);
              return (
                <motion.button
                  key={tag.id}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all border ${
                    isActive
                      ? 'text-white border-transparent'
                      : 'text-gray-600 border-gray-200 bg-white hover:border-gray-300'
                  }`}
                  style={
                    isActive
                      ? { backgroundColor: category.color }
                      : undefined
                  }
                  onClick={() => onTagSelect(tag.name)}
                  whileTap={{ scale: 0.97 }}
                >
                  {tag.name}
                  <span className={`ml-1 ${isActive ? 'opacity-70' : 'text-gray-400'}`}>
                    {tag.count}
                  </span>
                </motion.button>
              );
            })}
        </div>
      ))}
    </div>
  );
}

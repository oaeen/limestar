import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassTag } from './ui/GlassTag';
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
  // Track expanded categories (all expanded by default)
  const [expandedCategories, setExpandedCategories] = useState<Set<number>>(
    () => new Set(categories.map((c) => c.id))
  );

  const toggleCategory = (categoryId: number) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(categoryId)) {
        next.delete(categoryId);
      } else {
        next.add(categoryId);
      }
      return next;
    });
  };

  // Filter categories with links
  const visibleCategories = categories.filter((c) => c.count > 0);

  return (
    <div className="space-y-3">
      {/* Selected Tags */}
      {selectedTags.length > 0 && (
        <motion.div
          className="flex items-center gap-2 flex-wrap"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <span className="text-sm text-gray-500">已选:</span>
          {selectedTags.map((tagName) => (
            <GlassTag
              key={tagName}
              name={tagName}
              active
              onClick={() => onTagSelect(tagName)}
            />
          ))}
          {onClearAll && (
            <button
              className="text-sm text-apple-blue hover:underline"
              onClick={onClearAll}
            >
              清除全部
            </button>
          )}
        </motion.div>
      )}

      {/* "All" button */}
      <div className="flex gap-2 flex-wrap">
        <GlassTag
          name="全部"
          active={selectedTags.length === 0}
          onClick={onClearAll}
        />
      </div>

      {/* Categories with tags */}
      <div className="space-y-2">
        {visibleCategories.map((category) => (
          <div key={category.id} className="space-y-1">
            {/* Category header */}
            <button
              className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              onClick={() => toggleCategory(category.id)}
            >
              <span
                className={`transition-transform ${
                  expandedCategories.has(category.id) ? 'rotate-90' : ''
                }`}
              >
                ▶
              </span>
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: category.color }}
              />
              <span>{category.name}</span>
              <span className="text-gray-400">({category.count})</span>
            </button>

            {/* Child tags */}
            <AnimatePresence>
              {expandedCategories.has(category.id) && (
                <motion.div
                  className="flex gap-2 flex-wrap pl-5"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  {category.tags
                    .filter((tag) => tag.count > 0)
                    .map((tag) => (
                      <GlassTag
                        key={tag.id}
                        name={tag.name}
                        color={tag.color}
                        count={tag.count}
                        active={selectedTags.includes(tag.name)}
                        onClick={() => onTagSelect(tag.name)}
                      />
                    ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
}

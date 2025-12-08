import { motion } from 'framer-motion';
import { GlassTag } from './ui/GlassTag';
import type { TagWithCount } from '../types';

interface TagFilterProps {
  tags: TagWithCount[];
  selectedTags: string[];
  onTagSelect: (tagName: string) => void;
  onClearAll?: () => void;
}

export function TagFilter({
  tags,
  selectedTags,
  onTagSelect,
  onClearAll,
}: TagFilterProps) {
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

      {/* All Tags */}
      <div className="flex gap-2 flex-wrap overflow-x-auto pb-2 -mb-2 scrollbar-hide">
        <GlassTag
          name="全部"
          active={selectedTags.length === 0}
          onClick={onClearAll}
        />
        {tags.map((tag) => (
          <GlassTag
            key={tag.id}
            name={tag.name}
            color={tag.color}
            count={tag.count}
            active={selectedTags.includes(tag.name)}
            onClick={() => onTagSelect(tag.name)}
          />
        ))}
      </div>
    </div>
  );
}

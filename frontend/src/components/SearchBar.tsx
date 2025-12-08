import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder = '搜索链接...',
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleClear = useCallback(() => {
    onChange('');
  }, [onChange]);

  return (
    <motion.div
      className="glass-search"
      initial={false}
      animate={{
        boxShadow: isFocused
          ? '0 4px 20px rgba(0, 0, 0, 0.1), 0 0 0 4px rgba(0, 122, 255, 0.15)'
          : '0 2px 10px rgba(0, 0, 0, 0.06)',
      }}
    >
      {/* Search Icon */}
      <motion.div
        className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none"
        animate={{
          color: isFocused ? '#007AFF' : 'rgba(0, 0, 0, 0.4)',
        }}
      >
        <Search size={20} />
      </motion.div>

      {/* Input */}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
      />

      {/* Clear Button */}
      {value && (
        <motion.button
          className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-black/5"
          onClick={handleClear}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
        >
          <X size={18} className="text-gray-400" />
        </motion.button>
      )}
    </motion.div>
  );
}

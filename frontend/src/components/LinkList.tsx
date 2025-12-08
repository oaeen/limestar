import { motion, AnimatePresence } from 'framer-motion';
import { LinkCard } from './LinkCard';
import { Inbox } from 'lucide-react';
import type { Link } from '../types';

interface LinkListProps {
  links: Link[];
  isLoading?: boolean;
  onTagClick?: (tagName: string) => void;
}

export function LinkList({ links, isLoading, onTagClick }: LinkListProps) {
  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="glass-card p-5 animate-pulse"
          >
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-gray-200 rounded-xl" />
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-full" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (links.length === 0) {
    return (
      <motion.div
        className="glass-card p-12 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Inbox size={48} className="mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-600 mb-2">
          暂无链接
        </h3>
        <p className="text-sm text-gray-400">
          通过命令行工具添加您的第一个链接
        </p>
      </motion.div>
    );
  }

  // Link list
  return (
    <motion.div
      className="space-y-4"
      initial="hidden"
      animate="show"
      variants={{
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: {
            staggerChildren: 0.06,
          },
        },
      }}
    >
      <AnimatePresence mode="popLayout">
        {links.map((link) => (
          <LinkCard
            key={link.id}
            link={link}
            onTagClick={onTagClick}
          />
        ))}
      </AnimatePresence>
    </motion.div>
  );
}

import { useState, forwardRef } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Globe, Star } from 'lucide-react';
import { GlassTag } from './ui/GlassTag';
import { ConfirmDialog } from './ui/ConfirmDialog';
import type { Link } from '../types';

interface LinkCardProps {
  link: Link;
  onTagClick?: (tagName: string) => void;
  onDelete?: (linkId: number) => void;
}

export const LinkCard = forwardRef<HTMLDivElement, LinkCardProps>(
  function LinkCard({ link, onTagClick, onDelete }, ref) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const handleDeleteConfirm = () => {
    onDelete?.(link.id);
    setShowDeleteConfirm(false);
  };

  return (
    <div ref={ref}>
      <motion.article
        className="glass-card glass-card-interactive p-4 md:p-5 relative"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        whileHover={{ y: -2 }}
        layout
      >
        {/* Star button - 常驻显示 */}
        {onDelete && (
          <motion.button
            className="absolute top-3 right-3 p-1.5 rounded-full bg-white/60 hover:bg-amber-50 transition-colors"
            onClick={() => setShowDeleteConfirm(true)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="取消收藏"
          >
            <Star
              size={15}
              className="text-amber-400 fill-amber-400"
            />
          </motion.button>
        )}

        <div className="flex gap-4">
          {/* Favicon */}
          <div className="flex-shrink-0">
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-white/80 shadow-sm flex items-center justify-center overflow-hidden">
              {link.favicon_url ? (
                <img
                  src={link.favicon_url}
                  alt=""
                  className="w-6 h-6 md:w-7 md:h-7 object-contain"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                  }}
                />
              ) : null}
              <Globe
                size={24}
                className={`text-gray-400 ${link.favicon_url ? 'hidden' : ''}`}
              />
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Header: Title + Domain */}
            <div className="flex items-start justify-between gap-2 mb-1 pr-8">
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-1.5 font-semibold text-gray-900 hover:text-apple-blue transition-colors line-clamp-1"
              >
                <span className="truncate">{link.title}</span>
                <ExternalLink
                  size={14}
                  className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                />
              </a>
              <span className="text-xs text-gray-400 flex-shrink-0">
                {link.domain}
              </span>
            </div>

            {/* Description */}
            {link.description && (
              <p className="text-sm text-gray-600 line-clamp-3 mb-2">
                {link.description}
              </p>
            )}

            {/* User Note */}
            {link.user_note && (
              <p className="text-sm text-gray-500 italic mb-2 line-clamp-1">
                "{link.user_note}"
              </p>
            )}

            {/* Footer: Tags + Date */}
            <div className="flex items-center justify-between gap-2 mt-2">
              {/* Tags */}
              <div className="flex gap-1.5 flex-wrap overflow-hidden">
                {link.tags.slice(0, 5).map((tag) => (
                  <GlassTag
                    key={tag.id}
                    name={tag.name}
                    color={tag.color}
                    onClick={() => onTagClick?.(tag.name)}
                  />
                ))}
                {link.tags.length > 5 && (
                  <span className="text-xs text-gray-400 self-center">
                    +{link.tags.length - 5}
                  </span>
                )}
              </div>

              {/* Date */}
              <span className="text-xs text-gray-400 flex-shrink-0">
                {formatDate(link.created_at)}
              </span>
            </div>
          </div>
        </div>
      </motion.article>

      {/* 确认对话框 */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="取消收藏"
        message={`确定要移除「${link.title}」吗？此操作不可撤销。`}
        confirmText="移除"
        cancelText="保留"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  );
});

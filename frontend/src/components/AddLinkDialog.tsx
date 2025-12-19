import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link2, FileText, Loader2 } from 'lucide-react';
import { GlassButton } from './ui/GlassButton';
import { linksAPI } from '../services/api';

interface AddLinkDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddLinkDialog({ isOpen, onClose, onSuccess }: AddLinkDialogProps) {
  const [url, setUrl] = useState('');
  const [userNote, setUserNote] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      setError('请输入链接地址');
      return;
    }

    // 简单的 URL 验证
    try {
      new URL(url.startsWith('http') ? url : `https://${url}`);
    } catch {
      setError('请输入有效的链接地址');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
      await linksAPI.create({
        url: normalizedUrl,
        user_note: userNote.trim() || undefined,
      });

      // 成功后重置表单
      setUrl('');
      setUserNote('');
      onSuccess();
    } catch {
      setError('添加失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setUrl('');
    setUserNote('');
    setError('');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />

          {/* Dialog */}
          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="glass-card p-6 max-w-md w-full mx-auto"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Link2 size={20} className="text-lime-600" />
                添加收藏
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* URL Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    链接地址 <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 rounded-xl bg-white/60 border border-gray-200 focus:border-lime-400 focus:ring-2 focus:ring-lime-100 outline-none transition-all"
                    autoFocus
                  />
                </div>

                {/* User Note Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    备注 <span className="text-gray-400">(可选)</span>
                  </label>
                  <div className="relative">
                    <FileText
                      size={16}
                      className="absolute left-3 top-3 text-gray-400"
                    />
                    <textarea
                      value={userNote}
                      onChange={(e) => setUserNote(e.target.value)}
                      placeholder="为什么收藏这个链接？"
                      rows={2}
                      className="w-full px-4 py-3 pl-10 rounded-xl bg-white/60 border border-gray-200 focus:border-lime-400 focus:ring-2 focus:ring-lime-100 outline-none transition-all resize-none"
                    />
                  </div>
                </div>

                {error && (
                  <motion.p
                    className="text-sm text-red-500"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    {error}
                  </motion.p>
                )}

                <div className="flex gap-3 justify-end pt-2">
                  <GlassButton
                    type="button"
                    variant="secondary"
                    onClick={handleClose}
                    disabled={isLoading}
                  >
                    取消
                  </GlassButton>
                  <GlassButton
                    type="submit"
                    disabled={isLoading || !url.trim()}
                  >
                    {isLoading ? (
                      <span className="flex items-center gap-2">
                        <Loader2 size={16} className="animate-spin" />
                        添加中...
                      </span>
                    ) : (
                      '添加收藏'
                    )}
                  </GlassButton>
                </div>
              </form>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

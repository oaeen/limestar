import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings } from 'lucide-react';
import { LoginDialog } from './LoginDialog';
import { useAuthContext } from '../contexts/AuthContext';

export function Header() {
  const { isAuthenticated, logout } = useAuthContext();
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <header className="px-4 py-4 md:px-6 md:py-5">
      <div className="max-w-3xl mx-auto flex justify-between items-center">
        {/* 左侧占位 */}
        <div className="w-10" />

        {/* Logo */}
        <h1
          className="text-2xl md:text-3xl font-bold tracking-tight"
          style={{
            background: 'linear-gradient(135deg, #84cc16 0%, #65a30d 50%, #facc15 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: '0 2px 10px rgba(132, 204, 22, 0.2)',
            fontFamily: '"Comic Sans MS", "Chalkboard", "Comic Neue", cursive, sans-serif',
          }}
        >
          LimeStar
        </h1>

        {/* 隐藏的认证按钮 - 右上角 */}
        <div
          className="relative w-10 h-10 flex items-center justify-center"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <AnimatePresence>
            {(isHovered || isAuthenticated) && (
              <motion.button
                className={`p-2 rounded-full transition-colors ${
                  isAuthenticated
                    ? 'bg-lime-100 text-lime-600 hover:bg-lime-200'
                    : 'bg-gray-100/50 text-gray-400 hover:bg-gray-200/50'
                }`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => isAuthenticated ? logout() : setShowLoginDialog(true)}
                title={isAuthenticated ? '退出管理模式' : '进入管理模式'}
              >
                <Settings size={18} />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* 登录对话框 */}
      <LoginDialog
        isOpen={showLoginDialog}
        onClose={() => setShowLoginDialog(false)}
      />
    </header>
  );
}

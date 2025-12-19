import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings } from 'lucide-react';
import { LoginDialog } from './LoginDialog';
import { useAuthContext } from '../contexts/AuthContext';

export function Header() {
  const { isAuthenticated, logout } = useAuthContext();
  const [showLoginDialog, setShowLoginDialog] = useState(false);

  return (
    <header className="px-4 py-4 md:px-6 md:py-5">
      <div className="max-w-3xl mx-auto">
        {/* Logo */}
        <h1
          className="text-2xl md:text-3xl font-bold tracking-tight text-center"
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

      </div>

      {/* 认证按钮 - 固定在网页右上角 */}
      <motion.button
        className={`fixed top-4 right-4 z-50 p-2 rounded-full transition-colors ${
          isAuthenticated
            ? 'text-lime-600 hover:text-lime-700'
            : 'text-gray-400 hover:text-gray-500'
        }`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => isAuthenticated ? logout() : setShowLoginDialog(true)}
        title={isAuthenticated ? '退出管理模式' : '进入管理模式'}
      >
        <Settings size={18} />
      </motion.button>

      {/* 登录对话框 */}
      <LoginDialog
        isOpen={showLoginDialog}
        onClose={() => setShowLoginDialog(false)}
      />
    </header>
  );
}

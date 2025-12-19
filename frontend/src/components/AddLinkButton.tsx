import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus } from 'lucide-react';
import { AddLinkDialog } from './AddLinkDialog';
import { useAuthContext } from '../contexts/AuthContext';

interface AddLinkButtonProps {
  onLinkAdded: () => void;
}

export function AddLinkButton({ onLinkAdded }: AddLinkButtonProps) {
  const { isAuthenticated } = useAuthContext();
  const [showDialog, setShowDialog] = useState(false);

  if (!isAuthenticated) return null;

  return (
    <>
      <AnimatePresence>
        <motion.button
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-lime-400 to-lime-600 text-white shadow-lg shadow-lime-500/30 flex items-center justify-center z-40"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setShowDialog(true)}
          title="添加收藏"
        >
          <Plus size={28} strokeWidth={2.5} />
        </motion.button>
      </AnimatePresence>

      <AddLinkDialog
        isOpen={showDialog}
        onClose={() => setShowDialog(false)}
        onSuccess={() => {
          setShowDialog(false);
          onLinkAdded();
        }}
      />
    </>
  );
}

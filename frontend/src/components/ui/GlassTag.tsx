import { motion } from 'framer-motion';

interface GlassTagProps {
  name: string;
  color?: string;
  count?: number;
  active?: boolean;
  onClick?: () => void;
}

export function GlassTag({
  name,
  color,
  count,
  active = false,
  onClick,
}: GlassTagProps) {
  return (
    <motion.button
      className={`glass-tag ${active ? 'active' : ''}`}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      style={
        active && color
          ? { backgroundColor: color, borderColor: color }
          : undefined
      }
    >
      <span>{name}</span>
      {count !== undefined && (
        <span className="opacity-70">({count})</span>
      )}
    </motion.button>
  );
}

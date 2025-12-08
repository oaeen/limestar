import { motion, HTMLMotionProps } from 'framer-motion';
import { forwardRef } from 'react';

interface GlassButtonProps extends HTMLMotionProps<'button'> {
  variant?: 'primary' | 'secondary';
}

export const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className = '', variant = 'primary', children, ...props }, ref) => {
    const variantClass =
      variant === 'secondary' ? 'glass-button-secondary' : '';

    return (
      <motion.button
        ref={ref}
        className={`glass-button ${variantClass} ${className}`}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.98 }}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);

GlassButton.displayName = 'GlassButton';

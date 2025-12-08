import { motion, HTMLMotionProps } from 'framer-motion';
import { forwardRef } from 'react';

interface GlassButtonProps extends HTMLMotionProps<'button'> {
  variant?: 'primary' | 'secondary' | 'danger';
}

export const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className = '', variant = 'primary', children, ...props }, ref) => {
    const variantClasses: Record<string, string> = {
      primary: '',
      secondary: 'glass-button-secondary',
      danger: 'glass-button-danger',
    };

    return (
      <motion.button
        ref={ref}
        className={`glass-button ${variantClasses[variant]} ${className}`}
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

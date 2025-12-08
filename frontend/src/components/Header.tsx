import { Star } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 glass-card rounded-none border-x-0 border-t-0 px-4 py-3 md:px-6 md:py-4">
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 md:w-9 md:h-9 rounded-lg bg-gradient-to-br from-lime-400 to-lime-500 flex items-center justify-center shadow-sm">
            <Star size={18} className="text-white fill-white" />
          </div>
          <h1 className="text-lg md:text-xl font-semibold text-gray-900">
            LimeStar
          </h1>
        </div>

        {/* Stats or actions could go here */}
        <div className="text-sm text-gray-500">
          链接收藏
        </div>
      </div>
    </header>
  );
}

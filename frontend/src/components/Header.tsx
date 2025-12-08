export function Header() {
  return (
    <header className="px-4 py-4 md:px-6 md:py-5">
      <div className="max-w-3xl mx-auto flex justify-center">
        {/* 可爱艺术字 Logo */}
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
          🍋 LimeStar
        </h1>
      </div>
    </header>
  );
}

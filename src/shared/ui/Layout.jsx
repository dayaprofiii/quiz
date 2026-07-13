export default function Layout({ user, setView, children }) {
  return (
    <main className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => setView('home')}>
          ★ QUIZLEET ★
        </button>
      </header>
      <div className="nav-strip">
        <nav className="main-nav" aria-label="Основная навигация">
          <button className="nav-link nav-link-left" onClick={() => setView(user ? 'profile' : 'login')}>ПРОФИЛЬ</button>
          <button className="nav-link" onClick={() => setView(user ? 'quizzes' : 'login')}>МОИ ВИКТОРИНЫ</button>
          <button className="nav-link nav-link-right" onClick={() => setView(user ? 'history' : 'login')}>ИСТОРИЯ</button>
        </nav>
      </div>
      {children}
    </main>
  );
}

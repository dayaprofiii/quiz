export default function Leaderboard({ room, title = 'ТАБЛИЦА ЛИДЕРОВ' }) {
  const rows = room?.leaderboard || [];

  return (
    <section className="leaderboard-screen">
      <h1 className="leaderboard-title">{title}</h1>
      <div className="leaderboard-panel">
        <div className="leaderboard-head">
          <span>ИМЯ ПОЛЬЗОВАТЕЛЯ</span>
          <span>ОЧКИ</span>
        </div>
        {rows.length ? (
          rows.map((player, index) => (
            <div className="leaderboard-row" key={player.id}>
              <span className={index === 0 ? 'leaderboard-gold' : index === 2 ? 'leaderboard-bronze' : ''}>
                {index + 1}. {player.name}
              </span>
              <strong className={index === 0 ? 'leaderboard-gold' : index === 2 ? 'leaderboard-bronze' : ''}>
                {player.score}
              </strong>
            </div>
          ))
        ) : (
          <p className="leaderboard-empty">Пока нет результатов</p>
        )}
        {rows.length > 10 && <p className="leaderboard-more">...</p>}
      </div>
    </section>
  );
}

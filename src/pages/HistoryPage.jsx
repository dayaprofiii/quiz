import { useMemo, useState } from 'react';

function formatDate(value) {
  return new Date(value).toLocaleDateString('ru-RU');
}

function findUserIndex(item, user) {
  return (item.leaderboard || []).findIndex((player) => player.id === user?.id || player.name === user?.name);
}

function getUserPlace(item, user) {
  if (item.organizerId === user?.id) return 'Организатор';
  return `${findUserIndex(item, user) + 1} место`;
}

function rowClass(index, player, user) {
  if (index === 0) return 'history-result-gold';
  if (player.id === user?.id || player.name === user?.name) return 'history-result-current';
  return '';
}

export default function HistoryPage({ history, user }) {
  const availableHistory = useMemo(
    () => history.filter((item) => item.organizerId === user?.id || findUserIndex(item, user) !== -1),
    [history, user]
  );
  const [selectedId, setSelectedId] = useState(null);
  const selected = useMemo(() => availableHistory.find((item) => item.id === selectedId), [availableHistory, selectedId]);

  if (selected) {
    const rows = selected.leaderboard || [];

    return (
      <section className="history-page history-info-page">
        <button className="history-back-button" onClick={() => setSelectedId(null)}>НАЗАД</button>
        <h1 className="history-info-title">Результат викторины</h1>
        <div className="history-result-panel">
          <div className="history-result-head">
            <span>ИМЯ ПОЛЬЗОВАТЕЛЯ</span>
            <span>ОЧКИ</span>
          </div>
          {rows.map((player, index) => (
            <div className="history-result-row" key={`${player.id}-${index}`}>
              <span className={rowClass(index, player, user)}>{index + 1}. {player.name}</span>
              <strong className={rowClass(index, player, user)}>{player.score}</strong>
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="history-page history-list-page">
      <h1 className="history-list-title">Мои пройденные викторины</h1>
      <div className="history-list">
        {availableHistory.map((item) => (
          <article className="history-card" key={item.id}>
            <div className="history-card-main">
              <h2>{item.quizTitle}</h2>
              <time>{formatDate(item.finishedAt)}</time>
            </div>
            <div className="history-card-side">
              <strong>{getUserPlace(item, user)}</strong>
              <button onClick={() => setSelectedId(item.id)}>ПОДРОБНЕЕ</button>
            </div>
          </article>
        ))}
        {!availableHistory.length && <p className="history-empty">История викторин пока пуста</p>}
      </div>
    </section>
  );
}

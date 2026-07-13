import QuestionStage from '../shared/ui/QuestionStage.jsx';
import Leaderboard from '../shared/ui/Leaderboard.jsx';

export default function OrganizerRoomPage({ room, onStart }) {
  if (room?.status === 'finished') {
    return <Leaderboard room={room} />;
  }

  if (room?.status === 'waiting') {
    return (
      <section className="room-page">
        <div className="waiting-panel">
          <p className="waiting-title">Ожидание участников</p>
          <div className="room-code">Код комнаты: <strong>{room.code}</strong></div>
          <div className="waiting-list">
            {(room.players || []).length ? (
              room.players.map((player) => <span key={player.id}>{player.name}</span>)
            ) : (
              <span>Участники пока не подключились</span>
            )}
          </div>
          <button className="button-success" onClick={onStart}>ЗАПУСТИТЬ КВИЗ</button>
        </div>
      </section>
    );
  }

  return (
    <section className="room-page">
      <QuestionStage room={room} />
    </section>
  );
}

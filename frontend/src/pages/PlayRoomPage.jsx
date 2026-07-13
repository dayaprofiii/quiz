import { useEffect, useState } from 'react';
import QuestionStage from '../shared/ui/QuestionStage.jsx';
import Leaderboard from '../shared/ui/Leaderboard.jsx';

export default function PlayRoomPage({ room, user, onAnswer }) {
  const [selected, setSelected] = useState([]);
  const [answerState, setAnswerState] = useState(null);
  const question = room?.question;

  useEffect(() => {
    setSelected([]);
    setAnswerState(null);
  }, [room?.question?.id]);

  function toggle(id) {
    if (answerState && answerState.type !== 'warning') return;
    if (answerState?.type === 'warning') setAnswerState(null);
    if (!question?.multi) {
      setSelected([id]);
      return;
    }
    setSelected((items) => (items.includes(id) ? items.filter((item) => item !== id) : [...items, id]));
  }

  async function submitAnswer() {
    if (!selected.length) {
      setAnswerState({ type: 'warning', text: 'Выберите вариант ответа' });
      return;
    }
    try {
      const submittedQuestionId = question?.id;
      const result = await onAnswer(selected);
      const nextQuestionId = result?.room?.question?.id;
      if (nextQuestionId && nextQuestionId !== submittedQuestionId) {
        setSelected([]);
        setAnswerState(null);
        return;
      }
      const points = result?.points ?? 0;
      setAnswerState({
        type: result?.isCorrect ? 'success' : 'error',
        text: result?.isCorrect ? `Ответ принят: +${points} очков` : 'Ответ принят'
      });
    } catch (err) {
      setAnswerState({ type: 'error', text: err.message });
    }
  }

  if (room?.status === 'finished') {
    return <Leaderboard room={room} />;
  }

  if (!question) {
    return (
      <section className="room-page">
        <div className="waiting-panel">
          <p className="waiting-title">Ожидание запуска</p>
          <div className="room-code">Код комнаты: <strong>{room?.code}</strong></div>
          <p className="waiting-subtitle">Организатор скоро запустит квиз</p>
        </div>
      </section>
    );
  }

  return (
    <section className="room-page">
      <QuestionStage room={room} selected={selected} onSelect={toggle} answered={Boolean(answerState && answerState.type !== 'warning')} />
      <button className="answer-submit" disabled={Boolean(answerState && answerState.type !== 'warning')} onClick={submitAnswer}>
        ОТВЕТИТЬ
      </button>
      {answerState && <p className={`answer-state answer-state-${answerState.type}`}>{answerState.text}</p>}
      <p className="player-name">Участник: {user.name}</p>
    </section>
  );
}

import { useEffect, useState } from 'react';

export default function QuestionStage({ room, selected = [], onSelect, answered = false }) {
  const question = room?.question;
  const [remaining, setRemaining] = useState(room?.remainingSeconds ?? question?.timeLimit ?? 0);

  useEffect(() => {
    setRemaining(room?.remainingSeconds ?? question?.timeLimit ?? 0);
  }, [room?.question?.id, room?.remainingSeconds, question?.timeLimit]);

  useEffect(() => {
    if (!question) return undefined;
    const timer = setInterval(() => setRemaining((value) => Math.max(0, value - 1)), 1000);
    return () => clearInterval(timer);
  }, [question?.id]);

  if (!question) {
    return <p className="stage-waiting">Участники подключаются к комнате. Вопрос появится после запуска.</p>;
  }

  const minutes = Math.floor(remaining / 60);
  const seconds = String(remaining % 60).padStart(2, '0');
  const isImageQuestion = question.type === 'image' && question.image;
  const imageCaption = question.imageCaption || question.title;

  return (
    <div className="question-stage">
      {isImageQuestion ? (
        <>
          <div className="question-image-frame">
            <img className="question-image" src={question.image} alt="" />
          </div>
          {imageCaption && <p className="question-title question-image-caption">{imageCaption}</p>}
        </>
      ) : (
        <>
          <h1 className="question-title">{question.title}</h1>
          {question.body && <p className="question-body">{question.body}</p>}
        </>
      )}

      <p className="question-timer-label">ВРЕМЯ НА ВОПРОС</p>
      <strong className="question-timer">{minutes}:{seconds}</strong>
      <div className="answer-grid">
        {question.answers.map((answer) => (
          <button
            key={answer.id}
            className={`answer-option ${selected.includes(answer.id) ? 'answer-option-selected' : ''}`}
            disabled={!onSelect || answered}
            onClick={() => onSelect?.(answer.id)}
          >
            {answer.text}
          </button>
        ))}
      </div>
    </div>
  );
}

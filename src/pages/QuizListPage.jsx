export default function QuizListPage({ quizzes, onCreate, onEdit, onLaunch }) {
  return (
    <section className="quiz-list-page">
      <h1 className="quiz-list-heading">Мои викторины</h1>
      <div className="quiz-tabs">
        <button className="button-primary">Список викторин</button>
        <button className="button-muted" onClick={onCreate}>Создать новый квиз</button>
      </div>
      <div className="quiz-list">
        {quizzes.map((quiz) => (
          <article className="quiz-card" key={quiz.id}>
            <div>
              <h2 className="quiz-card-title">{quiz.title}</h2>
              <p className="quiz-card-meta">{quiz.questions.length} вопросов</p>
            </div>
            <div className="quiz-card-actions">
              <button className="button-success" onClick={() => onLaunch(quiz)}>Запустить</button>
              <button className="button-muted" onClick={() => onEdit(quiz)}>Изменить</button>
            </div>
          </article>
        ))}
        {!quizzes.length && <p className="quiz-list-empty">Пока нет созданных викторин</p>}
      </div>
    </section>
  );
}

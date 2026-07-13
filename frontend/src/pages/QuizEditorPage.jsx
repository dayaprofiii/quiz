import { useState } from 'react';
import { emptyQuestion, validateQuestion } from '../shared/lib/quiz.js';

const answerLabels = ['Первый', 'Второй', 'Третий', 'Четвертый'];
const maxImageSize = 4 * 1024 * 1024;

function cloneQuestion(question) {
  return {
    ...question,
    answers: question.answers.map((answer) => ({ ...answer }))
  };
}

export default function QuizEditorPage({ quiz, onSave, onCancel }) {
  const [draft, setDraft] = useState(() => ({ ...quiz, questions: quiz.questions?.length ? quiz.questions : [] }));
  const [mode, setMode] = useState('list');
  const [editingIndex, setEditingIndex] = useState(null);
  const [questionDraft, setQuestionDraft] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [questionError, setQuestionError] = useState('');
  const [deleteIndex, setDeleteIndex] = useState(null);

  function openQuestion(index) {
    setEditingIndex(index);
    setQuestionDraft(index === null ? emptyQuestion() : cloneQuestion(draft.questions[index]));
    setUploadError('');
    setUploadStatus('');
    setQuestionError('');
    setMode('question');
  }

  function updateQuestion(patch) {
    setQuestionDraft((question) => ({ ...question, ...patch }));
    setQuestionError('');
  }

  function updateAnswer(answerIndex, patch) {
    updateQuestion({
      answers: questionDraft.answers.map((answer, index) => (index === answerIndex ? { ...answer, ...patch } : answer))
    });
  }

  function updateCorrectAnswer(answerIndex, checked) {
    if (questionDraft.multi) {
      updateAnswer(answerIndex, { correct: checked });
      return;
    }
    updateQuestion({
      answers: questionDraft.answers.map((answer, index) => ({ ...answer, correct: index === answerIndex }))
    });
  }

  function updateMulti(nextMulti) {
    const firstCorrectIndex = Math.max(0, questionDraft.answers.findIndex((answer) => answer.correct));
    updateQuestion({
      multi: nextMulti,
      answers: nextMulti
        ? questionDraft.answers
        : questionDraft.answers.map((answer, index) => ({ ...answer, correct: index === firstCorrectIndex }))
    });
  }

  function uploadImage(file) {
    setUploadError('');
    setUploadStatus('');
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setUploadError('Загрузите файл изображения.');
      return;
    }
    if (file.size > maxImageSize) {
      setUploadError('Изображение слишком большое. Максимум 4 МБ.');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result !== 'string') {
        setUploadError('Не удалось прочитать изображение.');
        return;
      }
      updateQuestion({ image: reader.result });
      setUploadStatus('Изображение загружено');
    };
    reader.onerror = () => setUploadError('Не удалось загрузить изображение. Попробуйте другой файл.');
    reader.readAsDataURL(file);
  }

  function saveQuestion() {
    const validationError = validateQuestion(questionDraft);
    if (validationError) {
      setQuestionError(validationError);
      return;
    }

    const normalizedQuestion = {
      ...questionDraft,
      title: questionDraft.title.trim(),
      body: String(questionDraft.body || '').trim(),
      imageCaption: String(questionDraft.imageCaption || '').trim(),
      answers: questionDraft.answers.map((answer) => ({ ...answer, text: answer.text.trim() }))
    };

    setDraft((current) => {
      if (editingIndex === null) {
        if (current.questions.some((question) => question.id === normalizedQuestion.id)) return current;
        return { ...current, questions: [...current.questions, normalizedQuestion] };
      }
      return {
        ...current,
        questions: current.questions.map((question, index) => (index === editingIndex ? normalizedQuestion : question))
      };
    });
    setQuestionDraft(null);
    setEditingIndex(null);
    setQuestionError('');
    setMode('list');
  }

  function cancelQuestion() {
    setQuestionDraft(null);
    setEditingIndex(null);
    setQuestionError('');
    setMode('list');
  }

  function deleteQuestion() {
    setDraft({ ...draft, questions: draft.questions.filter((_, index) => index !== deleteIndex) });
    setDeleteIndex(null);
  }

  if (mode === 'question' && questionDraft) {
    return (
      <section className="editor-page">
        <h1 className="editor-title">{editingIndex === null ? 'Новый вопрос' : 'Редактирование вопроса'}</h1>
        <div className="question-editor-panel">
          <label className="editor-row">
            <span>Название вопроса</span>
            <input className="editor-field" value={questionDraft.title} onChange={(event) => updateQuestion({ title: event.target.value })} />
          </label>

          <label className="editor-row">
            <span>Тип вопроса</span>
            <select className="editor-field" value={questionDraft.type} onChange={(event) => updateQuestion({ type: event.target.value })}>
              <option value="text">Текстовый</option>
              <option value="image">Изображение</option>
            </select>
          </label>

          <label className="editor-row editor-row-checkbox">
            <span>Мультивыбор</span>
            <input className="editor-checkbox" type="checkbox" checked={questionDraft.multi} onChange={(event) => updateMulti(event.target.checked)} />
          </label>

          {questionDraft.type === 'image' ? (
            <>
              <div className="editor-upload">
                <label className="image-upload-button">
                  Загрузить изображение
                  <input className="sr-only" type="file" accept="image/*" onChange={(event) => uploadImage(event.target.files?.[0])} />
                </label>
                {uploadStatus && <p className="image-upload-status">{uploadStatus}</p>}
                {uploadError && <p className="image-upload-error">{uploadError}</p>}
              </div>
              <label className="editor-textarea-label">
                <span>Добавьте подпись</span>
                <textarea className="editor-textarea editor-caption" value={questionDraft.imageCaption || ''} onChange={(event) => updateQuestion({ imageCaption: event.target.value })} />
              </label>
            </>
          ) : (
            <label className="editor-textarea-label">
              <span>Введите текст вопроса</span>
              <textarea className="editor-textarea" value={questionDraft.body || ''} onChange={(event) => updateQuestion({ body: event.target.value })} />
            </label>
          )}

          {questionDraft.answers.map((answer, index) => (
            <label className="editor-row" key={answer.id}>
              <span>{answerLabels[index]} ответ</span>
              <input className="editor-field" value={answer.text} onChange={(event) => updateAnswer(index, { text: event.target.value })} />
            </label>
          ))}

          <div className="editor-row">
            <span>Правильные ответы</span>
            <div className="correct-list">
              {questionDraft.answers.map((answer, index) => (
                <label key={answer.id}>
                  <span>{answerLabels[index]}</span>
                  <input
                    type={questionDraft.multi ? 'checkbox' : 'radio'}
                    name="correct-answer"
                    checked={answer.correct}
                    onChange={(event) => updateCorrectAnswer(index, event.target.checked)}
                  />
                </label>
              ))}
            </div>
          </div>

          <label className="editor-row">
            <span>Время на ответ (секунды)</span>
            <input className="editor-field" type="number" min="5" value={questionDraft.timeLimit} onChange={(event) => updateQuestion({ timeLimit: Number(event.target.value) })} />
          </label>

          {questionError && <p className="image-upload-error">{questionError}</p>}

          <div className="editor-actions">
            <button className="button-danger" onClick={cancelQuestion}>НАЗАД</button>
            <button className="button-success" onClick={saveQuestion}>СОХРАНИТЬ</button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="editor-page">
      <div className="quiz-tabs">
        <button className="button-muted" onClick={onCancel}>Список викторин</button>
        <button className="button-primary">Создать новый квиз</button>
      </div>

      <label className="quiz-title-row">
        <span>Название викторины</span>
        <input className="editor-field" value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} />
      </label>

      <p className="question-list-title">Список вопросов</p>
      <div className="question-list">
        {draft.questions.map((item, index) => (
          <article className="question-card" key={item.id}>
            <div>
              <p className="question-card-title">{item.title || (index === 0 ? 'Первая загадка' : 'Вторая загадка')}</p>
              <div className="question-tags">
                <span className={`tag ${item.type === 'image' ? 'tag-image' : 'tag-text'}`}>{item.type === 'image' ? 'Изображение' : 'Текстовый'}</span>
                <span className={`tag ${item.multi ? 'tag-multi' : 'tag-single'}`}>{item.multi ? 'Мультивыбор' : 'Один ответ'}</span>
              </div>
            </div>
            <div className="question-card-actions">
              <button className="button-muted" onClick={() => openQuestion(index)}>Изменить</button>
              <button className="button-danger" onClick={() => setDeleteIndex(index)}>Удалить</button>
            </div>
          </article>
        ))}
      </div>

      <button className="add-question-button" onClick={() => openQuestion(null)}>
        Добавить вопрос
      </button>
      <button className="save-quiz-button" onClick={() => onSave(draft)}>СОХРАНИТЬ</button>

      {deleteIndex !== null && (
        <div className="error-overlay">
          <div className="error-modal">
            <h1>ОШИБКА</h1>
            <p>Удалить вопрос?</p>
            <div className="confirm-actions">
              <button onClick={deleteQuestion}>ДА</button>
              <button onClick={() => setDeleteIndex(null)}>НЕТ</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

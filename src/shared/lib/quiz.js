export function normalizeCode(code) {
  return String(code || '').trim().toUpperCase();
}

export function emptyQuestion() {
  return {
    id: crypto.randomUUID(),
    title: '',
    type: 'text',
    image: '',
    imageCaption: '',
    multi: false,
    timeLimit: 45,
    answers: [
      { id: crypto.randomUUID(), text: '', correct: true },
      { id: crypto.randomUUID(), text: '', correct: false },
      { id: crypto.randomUUID(), text: '', correct: false },
      { id: crypto.randomUUID(), text: '', correct: false }
    ]
  };
}

export function validateQuestion(question) {
  if (!String(question?.title || '').trim()) return 'Введите название вопроса.';
  if (question.type === 'text' && !String(question.body || '').trim()) return 'Введите текст вопроса.';
  if (question.type === 'image' && !String(question.image || '').trim()) return 'Загрузите изображение для вопроса.';
  if (!Array.isArray(question.answers) || question.answers.length < 2) return 'Добавьте минимум два ответа.';
  if (question.answers.some((answer) => !String(answer.text || '').trim())) return 'Заполните все варианты ответа.';
  const correctCount = question.answers.filter((answer) => answer.correct).length;
  if (!correctCount) return 'Отметьте правильный ответ.';
  if (!question.multi && correctCount !== 1) return 'Для вопроса с одним ответом выберите ровно один правильный вариант.';
  if (!Number(question.timeLimit) || Number(question.timeLimit) < 5) return 'Время на ответ должно быть не меньше 5 секунд.';
  return '';
}

export function validateQuiz(quiz) {
  const title = String(quiz.title || '').trim();
  if (!title) return 'Введите название викторины.';
  if (!quiz.questions.length) return 'Добавьте хотя бы один вопрос.';
  const questionError = quiz.questions.map(validateQuestion).find(Boolean);
  if (questionError) return questionError;
  return '';
}

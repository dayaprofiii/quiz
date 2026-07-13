from fastapi import HTTPException, status


def validate_question(question: dict) -> None:
    if not str(question.get('title') or '').strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Заполните название каждого вопроса.')
    if question.get('type') == 'text' and not str(question.get('body') or '').strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Заполните текст каждого текстового вопроса.')
    if question.get('type') == 'image' and not str(question.get('image') or '').strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Для вопроса с изображением загрузите изображение.')
    answers = question.get('answers')
    if not isinstance(answers, list) or len(answers) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'У каждого вопроса должно быть минимум два ответа.')
    if any(not str(answer.get('text') or '').strip() for answer in answers):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Заполните текст всех ответов.')
    correct_count = len([answer for answer in answers if answer.get('correct')])
    if correct_count == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'У каждого вопроса должен быть правильный ответ.')
    if not question.get('multi') and correct_count != 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'В вопросе с одним ответом должен быть выбран ровно один правильный вариант.')
    if int(question.get('timeLimit') or 0) < 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Время на ответ должно быть не меньше 5 секунд.')


def validate_quiz_payload(payload: dict) -> None:
    if not str(payload.get('title') or '').strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Введите название викторины.')
    questions = payload.get('questions')
    if not isinstance(questions, list) or not questions:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Добавьте хотя бы один вопрос.')
    for question in questions:
        validate_question(question)

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.quiz_validation import validate_quiz_payload
from app.services.rooms import room_manager


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_http_errors_use_message_contract():
    @app.get('/__test_error__', include_in_schema=False)
    async def test_error():
        raise HTTPException(status_code=418, detail='Проверка ошибки.')

    with TestClient(app) as client:
        response = client.get('/__test_error__')

    assert response.status_code == 418
    assert response.json() == {'message': 'Проверка ошибки.'}


def test_validation_errors_are_user_friendly_russian():
    with TestClient(app) as client:
        response = client.post('/api/auth/login', json={})

    assert response.status_code == 422
    assert response.json() == {'message': 'Заполните поле «электронная почта».'}


def test_quiz_validation_rejects_empty_question():
    try:
        validate_quiz_payload({'title': 'Квиз', 'questions': [{'title': '', 'answers': []}]})
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == 'Заполните название каждого вопроса.'
    else:
        raise AssertionError('empty question should be rejected')


async def _run_room_flow():
    quiz = {
        'id': 'test-quiz',
        'title': 'Test',
        'timeLimit': 30,
        'questions': [
            {
                'id': 'q1',
                'title': 'Question',
                'type': 'text',
                'body': 'Body',
                'multi': False,
                'timeLimit': 30,
                'answers': [
                    {'id': 'a1', 'text': 'A', 'correct': True},
                    {'id': 'a2', 'text': 'B', 'correct': False},
                ],
            }
        ],
    }
    room = room_manager.create(quiz, 'organizer')
    await room_manager.join(room.code, 'player', 'Player')
    await room_manager.start(room.code)
    return await room_manager.answer(room.code, 'player', ['a1'])


def test_room_flow_scores_correct_answer():
    import asyncio

    is_correct, score, room, points = asyncio.run(_run_room_flow())
    assert is_correct is True
    assert 1 <= points <= 100
    assert score == points
    assert room.snapshot()['leaderboard'][0]['score'] == points

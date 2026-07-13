from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import Quiz, User
from app.schemas.quiz import QuizListResponse, QuizPayload, QuizResponse
from app.services.quiz_validation import validate_quiz_payload
from app.services.serializers import serialize_quiz


router = APIRouter(prefix='/quizzes', tags=['quizzes'])


def normalized_quiz_data(payload: QuizPayload) -> dict:
    data = payload.model_dump(mode='json')
    validate_quiz_payload(data)
    return data


@router.get('', response_model=QuizListResponse)
async def list_quizzes(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(Quiz).order_by(Quiz.created_at.desc()))
    return {'quizzes': [serialize_quiz(quiz) for quiz in result.all()]}


@router.post('', response_model=QuizResponse)
async def create_quiz(payload: QuizPayload, session: AsyncSession = Depends(get_session)):
    data = normalized_quiz_data(payload)
    owner = await session.get(User, data['ownerId'])
    if not owner:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Пользователь не найден.')

    quiz = Quiz(
        id=str(uuid4()),
        owner_id=data['ownerId'],
        title=data['title'].strip(),
        category=(data.get('category') or 'Общее').strip(),
        time_limit=data.get('timeLimit') or 45,
        rules=(data.get('rules') or '').strip(),
        questions=data.get('questions') or [],
    )
    session.add(quiz)
    await session.commit()
    await session.refresh(quiz)
    return {'quiz': serialize_quiz(quiz)}


@router.put('/{quiz_id}', response_model=QuizResponse)
async def update_quiz(quiz_id: str, payload: QuizPayload, session: AsyncSession = Depends(get_session)):
    data = normalized_quiz_data(payload)
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Квиз не найден.')
    if quiz.owner_id != data['ownerId']:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Можно редактировать только свои викторины.')

    quiz.title = data['title'].strip()
    quiz.category = (data.get('category') or 'Общее').strip()
    quiz.time_limit = data.get('timeLimit') or 45
    quiz.rules = (data.get('rules') or '').strip()
    quiz.questions = data.get('questions') or []
    await session.commit()
    await session.refresh(quiz)
    return {'quiz': serialize_quiz(quiz)}

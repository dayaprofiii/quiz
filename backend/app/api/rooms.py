from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import History, Quiz
from app.schemas.room import AnswerResponse, AnswerRoomPayload, CreateRoomPayload, CreateRoomResponse, JoinRoomPayload, JoinRoomResponse, RoomResponse
from app.services.rooms import leaderboard, room_manager
from app.services.serializers import serialize_quiz


router = APIRouter(prefix='/rooms', tags=['rooms'])


async def save_room_history(session: AsyncSession, room) -> None:
    history = History(
        id=str(uuid4()),
        quiz_id=room.quiz['id'],
        organizer_id=room.organizer_id,
        quiz_title=room.quiz['title'],
        code=room.code,
        finished_at=datetime.now(timezone.utc),
        leaderboard=leaderboard(room),
    )
    session.add(history)
    await session.commit()


@router.post('', response_model=CreateRoomResponse)
async def create_room(payload: CreateRoomPayload, session: AsyncSession = Depends(get_session)):
    quiz = await session.get(Quiz, payload.quizId)
    if not quiz:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Квиз не найден.')
    room = room_manager.create(serialize_quiz(quiz), payload.organizerId)
    return {'code': room.code, 'room': room.snapshot()}


@router.get('/{code}', response_model=RoomResponse)
async def get_room(code: str):
    room = room_manager.get(code)
    return {'room': room.snapshot()}


@router.post('/{code}/join', response_model=JoinRoomResponse)
async def join_room(code: str, payload: JoinRoomPayload):
    player, room = await room_manager.join(code, payload.userId, payload.name)
    return {'player': player, 'room': room.snapshot()}


@router.post('/{code}/start', response_model=RoomResponse)
async def start_room(code: str):
    room = await room_manager.start(code)
    return {'room': room.snapshot()}


@router.post('/{code}/next', response_model=RoomResponse)
async def next_room_question(code: str, session: AsyncSession = Depends(get_session)):
    room, finished = await room_manager.next_question(code)
    if finished:
        await save_room_history(session, room)
    return {'room': room.snapshot()}


@router.post('/{code}/answer', response_model=AnswerResponse)
async def answer_room_question(code: str, payload: AnswerRoomPayload, session: AsyncSession = Depends(get_session)):
    is_correct, score, room, points = await room_manager.answer(code, payload.userId, payload.answerIds)
    if room_manager.all_players_answered(room):
        room, finished = await room_manager.next_question(code)
        if finished:
            await save_room_history(session, room)
    return {'isCorrect': is_correct, 'score': score, 'points': points, 'room': room.snapshot()}

import random
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, WebSocket, status
from starlette.websockets import WebSocketState


ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def normalize_room_code(value: str | None) -> str:
    return str(value or '').strip().upper()


def make_room_code() -> str:
    return ''.join(random.choice(ALPHABET) for _ in range(5))


def leaderboard(room: 'Room') -> list[dict[str, Any]]:
    return sorted(
        [{'id': player['id'], 'name': player['name'], 'score': player['score']} for player in room.players.values()],
        key=lambda player: (-player['score'], player['name']),
    )


def sanitize_question(question: dict | None) -> dict | None:
    if not question:
        return None
    return {
        'id': question.get('id'),
        'title': question.get('title'),
        'type': question.get('type'),
        'image': question.get('image'),
        'imageCaption': question.get('imageCaption'),
        'multi': bool(question.get('multi')),
        'timeLimit': question.get('timeLimit'),
        'body': question.get('body'),
        'answers': [{'id': answer.get('id'), 'text': answer.get('text')} for answer in question.get('answers', [])],
    }


@dataclass
class Room:
    code: str
    quiz: dict[str, Any]
    organizer_id: str
    status: str = 'waiting'
    current_index: int = -1
    deadline: datetime | None = None
    players: dict[str, dict[str, Any]] = field(default_factory=dict)
    answers: dict[str, dict[str, Any]] = field(default_factory=dict)
    clients: set[WebSocket] = field(default_factory=set)

    def snapshot(self) -> dict[str, Any]:
        question = self.quiz['questions'][self.current_index] if 0 <= self.current_index < len(self.quiz['questions']) else None
        remaining_seconds = None
        if self.deadline:
            remaining_seconds = max(0, int((self.deadline - datetime.now(timezone.utc)).total_seconds() + 0.999))
        return {
            'code': self.code,
            'quizId': self.quiz['id'],
            'quizTitle': self.quiz['title'],
            'organizerId': self.organizer_id,
            'status': self.status,
            'currentIndex': self.current_index,
            'totalQuestions': len(self.quiz['questions']),
            'question': sanitize_question(question) if self.status == 'running' else None,
            'remainingSeconds': remaining_seconds,
            'leaderboard': leaderboard(self),
            'players': [{'id': player['id'], 'name': player['name']} for player in self.players.values()],
        }


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}

    def create(self, quiz: dict[str, Any], organizer_id: str) -> Room:
        if not quiz.get('questions'):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Нельзя запустить квиз без вопросов.')
        code = make_room_code()
        while code in self.rooms:
            code = make_room_code()
        room = Room(code=code, quiz=quiz, organizer_id=organizer_id)
        self.rooms[code] = room
        return room

    def get(self, code: str) -> Room:
        room = self.rooms.get(normalize_room_code(code))
        if not room:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Комната не найдена.')
        return room

    async def connect(self, websocket: WebSocket, code: str) -> Room:
        room = self.get(code)
        await websocket.accept()
        room.clients.add(websocket)
        await websocket.send_json({'type': 'room', 'room': room.snapshot()})
        return room

    def disconnect(self, room: Room, websocket: WebSocket) -> None:
        room.clients.discard(websocket)

    async def broadcast(self, room: Room) -> None:
        payload = {'type': 'room', 'room': room.snapshot()}
        disconnected: list[WebSocket] = []
        for client in list(room.clients):
            if client.client_state != WebSocketState.CONNECTED:
                disconnected.append(client)
                continue
            try:
                await client.send_json(payload)
            except RuntimeError:
                disconnected.append(client)
        for client in disconnected:
            room.clients.discard(client)

    async def join(self, code: str, user_id: str | None, name: str | None) -> tuple[dict[str, Any], Room]:
        room = self.get(code)
        player_id = user_id or str(uuid4())
        if player_id not in room.players:
            room.players[player_id] = {'id': player_id, 'name': name or 'Player', 'score': 0}
        await self.broadcast(room)
        return room.players[player_id], room

    async def start(self, code: str) -> Room:
        room = self.get(code)
        if room.status == 'running':
            raise HTTPException(status.HTTP_409_CONFLICT, 'Квиз уже запущен.')
        if room.status == 'finished':
            raise HTTPException(status.HTTP_409_CONFLICT, 'Квиз уже завершён.')
        if not room.quiz.get('questions'):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Нельзя запустить квиз без вопросов.')
        room.status = 'running'
        room.current_index = 0
        room.answers.clear()
        seconds = room.quiz['questions'][0].get('timeLimit') or room.quiz.get('timeLimit') or 45
        room.deadline = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        await self.broadcast(room)
        return room

    async def next_question(self, code: str) -> tuple[Room, bool]:
        room = self.get(code)
        if room.status == 'waiting':
            raise HTTPException(status.HTTP_409_CONFLICT, 'Сначала запустите квиз.')
        if room.status == 'finished':
            raise HTTPException(status.HTTP_409_CONFLICT, 'Квиз уже завершён.')
        finished = room.current_index + 1 >= len(room.quiz['questions'])
        if finished:
            room.status = 'finished'
            room.deadline = None
        else:
            room.current_index += 1
            room.answers.clear()
            seconds = room.quiz['questions'][room.current_index].get('timeLimit') or room.quiz.get('timeLimit') or 45
            room.deadline = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        await self.broadcast(room)
        return room, finished

    async def answer(self, code: str, user_id: str, answer_ids: list[str]) -> tuple[bool, int, Room]:
        room = self.get(code)
        if room.status != 'running':
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Активный вопрос не найден.')
        player = room.players.get(user_id)
        question = room.quiz['questions'][room.current_index] if 0 <= room.current_index < len(room.quiz['questions']) else None
        if not player or not question:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Участник или вопрос не найден.')
        if not answer_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Выберите вариант ответа.')
        if not question.get('multi') and len(answer_ids) > 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'В этом вопросе можно выбрать только один ответ.')
        if room.deadline and datetime.now(timezone.utc) > room.deadline:
            raise HTTPException(status.HTTP_409_CONFLICT, 'Время на ответ истекло.')
        if player['id'] in room.answers:
            raise HTTPException(status.HTTP_409_CONFLICT, 'Ответ уже принят.')

        selected = sorted(answer_ids)
        correct = sorted(answer['id'] for answer in question.get('answers', []) if answer.get('correct'))
        is_correct = len(selected) == len(correct) and all(answer_id == correct[index] for index, answer_id in enumerate(selected))
        total_seconds = question.get('timeLimit') or room.quiz.get('timeLimit') or 45
        remaining_seconds = 0
        if room.deadline:
            remaining_seconds = max(0, (room.deadline - datetime.now(timezone.utc)).total_seconds())
        points = max(10, min(100, round((remaining_seconds / total_seconds) * 100))) if is_correct else 0
        if is_correct:
            player['score'] += points
        room.answers[player['id']] = {'questionId': question['id'], 'selected': selected, 'isCorrect': is_correct}
        await self.broadcast(room)
        return is_correct, player['score'], room, points


room_manager = RoomManager()

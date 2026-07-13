from typing import Any

from pydantic import BaseModel


class CreateRoomPayload(BaseModel):
    quizId: str
    organizerId: str


class JoinRoomPayload(BaseModel):
    userId: str | None = None
    name: str | None = None


class AnswerRoomPayload(BaseModel):
    userId: str
    answerIds: list[str]


class RoomResponse(BaseModel):
    room: dict[str, Any]


class CreateRoomResponse(RoomResponse):
    code: str


class JoinRoomResponse(RoomResponse):
    player: dict[str, Any]


class AnswerResponse(RoomResponse):
    isCorrect: bool
    score: int
    points: int

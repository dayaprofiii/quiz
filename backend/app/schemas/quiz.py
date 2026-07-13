from typing import Any, Literal

from pydantic import BaseModel, Field


class AnswerPayload(BaseModel):
    id: str
    text: str
    correct: bool = False


class QuestionPayload(BaseModel):
    id: str
    title: str
    type: Literal['text', 'image'] = 'text'
    image: str | None = ''
    imageCaption: str | None = ''
    multi: bool = False
    timeLimit: int = Field(default=45, ge=5)
    body: str | None = ''
    answers: list[AnswerPayload]


class QuizPayload(BaseModel):
    id: str | None = None
    ownerId: str
    title: str
    category: str | None = 'Общее'
    timeLimit: int | None = Field(default=45, ge=5)
    rules: str | None = ''
    questions: list[QuestionPayload]


class QuizOut(BaseModel):
    id: str
    ownerId: str
    title: str
    category: str
    timeLimit: int
    rules: str
    questions: list[dict[str, Any]]


class QuizListResponse(BaseModel):
    quizzes: list[QuizOut]


class QuizResponse(BaseModel):
    quiz: QuizOut

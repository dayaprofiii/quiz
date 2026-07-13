from typing import Any

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: str
    quizId: str | None
    organizerId: str | None
    quizTitle: str
    code: str
    finishedAt: str
    leaderboard: list[dict[str, Any]]


class HistoryResponse(BaseModel):
    history: list[HistoryItem]

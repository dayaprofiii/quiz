from datetime import datetime, timezone
from typing import Any

from app.models.entities import History, Quiz, User


def serialize_user(user: User) -> dict[str, Any]:
    return {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
    }


def serialize_quiz(quiz: Quiz) -> dict[str, Any]:
    return {
        'id': quiz.id,
        'ownerId': quiz.owner_id,
        'title': quiz.title,
        'category': quiz.category,
        'timeLimit': quiz.time_limit,
        'rules': quiz.rules,
        'questions': quiz.questions or [],
    }


def serialize_history(item: History, current_names: dict[str, str] | None = None) -> dict[str, Any]:
    finished_at = item.finished_at
    if isinstance(finished_at, datetime) and finished_at.tzinfo is None:
        finished_at = finished_at.replace(tzinfo=timezone.utc)
    leaderboard = []
    for player in item.leaderboard or []:
        player_data = dict(player)
        player_id = str(player_data.get('id') or '')
        if current_names and player_id in current_names:
            player_data['name'] = current_names[player_id]
        leaderboard.append(player_data)
    return {
        'id': item.id,
        'quizId': item.quiz_id,
        'organizerId': item.organizer_id,
        'quizTitle': item.quiz_title,
        'code': item.code,
        'finishedAt': finished_at.isoformat() if isinstance(finished_at, datetime) else str(finished_at),
        'leaderboard': leaderboard,
    }

from fastapi import APIRouter

from app.api import auth, history, quizzes, rooms, users


api_router = APIRouter(prefix='/api')
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(quizzes.router)
api_router.include_router(rooms.router)
api_router.include_router(history.router)

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.db.session import get_session
from app.models.entities import User
from app.schemas.auth import AuthPayload, AuthResponse, RegisterPayload
from app.services.serializers import serialize_user


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=AuthResponse)
async def register(payload: RegisterPayload, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, 'Пользователь уже существует.')

    user = User(
        id=str(uuid4()),
        email=payload.email.lower(),
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
        role='user',
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {'user': serialize_user(user)}


@router.post('/login', response_model=AuthResponse)
async def login(payload: AuthPayload, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Неверная почта или пароль.')
    return {'user': serialize_user(user)}

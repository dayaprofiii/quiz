from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.db.session import get_session
from app.models.entities import User
from app.schemas.auth import AuthResponse, UserUpdatePayload
from app.services.serializers import serialize_user


router = APIRouter(prefix='/users', tags=['users'])


@router.put('/{user_id}', response_model=AuthResponse)
async def update_user(user_id: str, payload: UserUpdatePayload, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Пользователь не найден.')

    if payload.email:
        next_email = payload.email.lower()
        duplicate = await session.scalar(select(User).where(User.email == next_email, User.id != user.id))
        if duplicate:
            raise HTTPException(status.HTTP_409_CONFLICT, 'Эта почта уже занята.')
        user.email = next_email

    if payload.name:
        user.name = payload.name.strip()

    current_password = payload.currentPassword or ''
    next_password = payload.nextPassword or ''
    has_profile_changes = bool(payload.email or payload.name or current_password or next_password)
    password_fields_sent = {'currentPassword', 'nextPassword'} & payload.model_fields_set
    if password_fields_sent and not current_password and not next_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Введите текущий и новый пароль.')
    if not has_profile_changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Введите новые данные для сохранения.')

    if current_password or next_password:
        if not current_password or not next_password:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Введите текущий и новый пароль.')
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Текущий пароль указан неверно.')
        if len(next_password) < 4:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Новый пароль должен быть не короче 4 символов.')
        user.password_hash = hash_password(next_password)

    await session.commit()
    await session.refresh(user)
    return {'user': serialize_user(user)}

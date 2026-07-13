from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default='user')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    quizzes: Mapped[list['Quiz']] = relationship(back_populates='owner')

    __table_args__ = (UniqueConstraint('email', name='uq_users_email'),)


class Quiz(Base):
    __tablename__ = 'quizzes'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(64), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False, default='Общее')
    time_limit: Mapped[int] = mapped_column(nullable=False, default=45)
    rules: Mapped[str] = mapped_column(Text, nullable=False, default='')
    questions: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner: Mapped[User] = relationship(back_populates='quizzes')


class History(Base):
    __tablename__ = 'history'

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    quiz_id: Mapped[str | None] = mapped_column(String(64), ForeignKey('quizzes.id', ondelete='SET NULL'), nullable=True, index=True)
    organizer_id: Mapped[str | None] = mapped_column(String(64), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    quiz_title: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    leaderboard: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import History
from app.schemas.history import HistoryResponse
from app.services.serializers import serialize_history


router = APIRouter(prefix='/history', tags=['history'])


@router.get('', response_model=HistoryResponse)
async def list_history(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(History).order_by(History.finished_at.desc()))
    return {'history': [serialize_history(item) for item in result.all()]}

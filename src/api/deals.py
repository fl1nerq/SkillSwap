from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import get_current_user
from src.database import get_db
from src.models.models import User, DealStatus
from src.schemas.schemas import DealCreate, DealRead
from src.services.deals import create_deal, accept_deal, deals_incoming, deals_outcoming

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealRead)
async def create_deal_endpoint(
        data: DealCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await create_deal(data, session, current_user)


@router.put("/{deal_id}")
async def accept_deal_endpoint(
        deal_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await accept_deal(deal_id, current_user, session)


@router.get("/incoming", response_model=list[DealRead])
async def deals_incoming_endpoint(
        status: Optional[DealStatus] = None,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),

):
    return await deals_incoming(status,current_user, session)


@router.get("/outcoming", response_model=list[DealRead])
async def deals_outcoming_endpoint(
        status: Optional[DealStatus] = None,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
   return await deals_outcoming(status, current_user, session)
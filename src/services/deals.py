from typing import Optional

from fastapi import Depends, APIRouter
from fastapi import HTTPException
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User, Ad, Deal, DealStatus
from src.schemas.schemas import DealCreate


async def create_deal(
        data: DealCreate,
        session: AsyncSession,
        current_user: User
):
    stmt = select(Ad.user_id).where(Ad.id == data.ad_id)
    result = await session.execute(stmt)
    receiver_id = result.scalars().first()

    if not receiver_id:
        raise HTTPException(status_code=404, detail="Ad not found")

    if current_user.id == receiver_id:
        raise HTTPException(
            status_code=403,
            detail="You can't make a deal with your own ad"
        )

    stmt = select(Deal).where(Deal.ad_id == data.ad_id, Deal.initiator_id == current_user.id)
    result = await session.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail="Deal already exists"
        )

    new_deal = Deal(
        ad_id=data.ad_id,
        initiator_id=current_user.id,
        receiver_id=receiver_id,
        status=DealStatus.PENDING
    )

    session.add(new_deal)
    await session.commit()
    await session.refresh(new_deal)

    return new_deal


async def accept_deal(
        deal_id: int,
        current_user: User,
        session: AsyncSession
):
    stmt = select(Deal.receiver_id).where(Deal.id == deal_id)
    result = await session.execute(stmt)
    receiver_id = result.scalars().first()

    if not receiver_id:
        raise HTTPException(status_code=404, detail="Deal not found")

    if current_user.id != receiver_id:
        raise HTTPException(status_code=403, detail="no suka")

    stmt = update(Deal).where(Deal.id == deal_id).values(status=DealStatus.IN_PROGRESS)
    await session.execute(stmt)
    await session.commit()

    return {"message": "accepted successfully"}


async def deals_incoming(
        status: DealStatus,
        current_user: User,
        session: AsyncSession
):
    stmt = select(Deal).where(Deal.receiver_id == current_user.id)

    if status:
        stmt = stmt.where(Deal.status == status)

    result = await session.execute(stmt)
    return result.scalars().all()


async def deals_outcoming(
        status: DealStatus,
        current_user: User,
        session: AsyncSession
):
    stmt = select(Deal).where(Deal.initiator_id == current_user.id)

    if status:
        stmt = stmt.where(Deal.status == status)

    result = await session.execute(stmt)
    return result.scalars().all()

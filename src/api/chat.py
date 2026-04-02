
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import get_current_user
from src.database import get_db
from src.models.models import Deal, Message, User
from src.schemas.schemas import MessageRead
from src.services.websockets import manager

router = APIRouter(prefix="/chat", tags=["chat"])

@router.websocket("/{deal_id}")
async def websocket_chat(
        websocket: WebSocket,
        deal_id: int,
        token: str = Query(...),
        session: AsyncSession = Depends(get_db)
):

    cur_user = await get_current_user(token, session)

    stmt = select(Deal.receiver_id, Deal.initiator_id).where(
        Deal.id == deal_id
    )
    result = await session.execute(stmt)

    row = result.first()
    if not row:
        await websocket.close(code=1008)
        return

    if cur_user.id not in row:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, deal_id)

    try:
        while True:

            data = await websocket.receive_text()

            new_message = Message(
                deal_id=deal_id,
                sender_id=cur_user.id,
                content=data
            )

            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)

            message_data = {
                "sender_id": cur_user.id,
                "content": data,
                "created_id": new_message.created_at.isoformat()
            }
            await manager.broadcast_to_deal(deal_id, message_data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, deal_id)


@router.get("/{deal_id}", response_model=list[MessageRead])
async def get_history_chat(
        deal_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    stmt = select(Deal.receiver_id, Deal.initiator_id).where(Deal.id == deal_id)
    result = await session.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Deal not found"
        )

    if current_user.id not in row:
        raise HTTPException(
            status_code=403,
            detail=""
        )

    stmt = select(Message).where(
        Message.deal_id == deal_id)
    result = await session.execute(stmt)

    return result.scalars().all()







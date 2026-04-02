import shutil
import uuid
from typing import Optional
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.security import get_current_user
from src.models.models import Ad, User, AdType, SortOrder, Category
from src.schemas.schemas import AdCreate, AdUpdate

UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def create_ad(data: AdCreate, session: AsyncSession, current_user: User) -> Ad:
    user_id = current_user.id

    if data.category_id:
        category = await session.get(Category, data.category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Такой категории не существует"
            )

    new_ad = Ad(
        title=data.title,
        description=data.description,
        type=data.type,
        category_id=data.category_id,
        user_id=user_id
    )

    session.add(new_ad)
    await session.commit()
    await session.refresh(new_ad)

    return new_ad


async def get_ads(
        limit: int,
        offset: int,
        category_id: int,
        type: AdType,
        sort: SortOrder,
        session: AsyncSession
):

    stmt = select(Ad).options(
        joinedload(Ad.user),
        joinedload(Ad.category)
    )

    if category_id:
        stmt = stmt.where(Ad.category_id==category_id)
    if type:
        stmt = stmt.where(Ad.type == type)

    if sort == SortOrder.NEWEST:
        stmt = stmt.order_by(Ad.created_at.desc())
    else:
        stmt = stmt.order_by(Ad.created_at.asc())

    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_ad(ad_id: int, session: AsyncSession, current_user: User):
    stmt = select(Ad).where(
        Ad.id == ad_id
    )
    result = await session.execute(stmt)
    ad = result.scalars().first()

    if not ad:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    if ad.user_id != current_user.id:
        raise HTTPException(
            status_code=409,
            detail="No access"
        )

    stmt = delete(Ad).where(
        Ad.id == ad_id
    )

    await session.execute(stmt)
    await session.commit()
    return {"message": "success"}


async def delete_ads(ad_id_list: list[int], session: AsyncSession, current_user: User):
    stmt = delete(Ad).where(
        Ad.id.in_(ad_id_list),
        Ad.user_id == current_user.id
    )

    await session.execute(stmt)
    await session.commit()

    return {"message": "success"}

async def edit_ad(ad_id: int, data: AdUpdate, session: AsyncSession, current_user: User):

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"message" : "Nothing to update"}

    stmt = update(Ad).where(
        Ad.id == ad_id,
        Ad.user_id == current_user.id
    ).values(**update_data)


    await session.execute(stmt)
    await session.commit()

    return {"message": "Updated successfully"}


async def upload_image(
        ad_id: int,
        file: UploadFile,
        current_user: User,
        session: AsyncSession
):
    stmt = select(Ad.user_id).where(Ad.id == ad_id)
    result = await session.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=404,  # 404 - Не найдено
            detail="Ad not found"
        )

    if current_user.id not in row:
        raise HTTPException(
            status_code=403,
            detail="No access"
        )

    file_type = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_type}"
    new_filepath = UPLOAD_DIR / new_filename

    with open(new_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    stmt = update(Ad).where(Ad.id == ad_id).values(
        image_url=f"static/images/{new_filename}"
    )
    await session.execute(stmt)
    await session.commit()

    return {"detail" : "Image uploaded successfully"}

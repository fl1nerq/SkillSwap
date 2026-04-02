from typing import Optional

import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import get_current_user
from src.database import get_db
from src.models.models import User, AdType, SortOrder, Ad
from src.schemas.schemas import AdCreate, AdReadFull, AdDelete, AdRead, AdUpdate
from src.services.ads import create_ad, get_ads, delete_ad, delete_ads, edit_ad, upload_image

router = APIRouter(prefix="/ads", tags=["ads"])

@router.post("")
async def create_ad_endpoint(
        data: AdCreate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await send_notification()
    return await create_ad(data, session, current_user)


@router.get("", response_model=list[AdReadFull])
async def get_ads_endpoint(
        limit: int = Query(10, ge=1, le=100, description="Максимум 100"),
        offset: int = Query(0, ge=0),
        category_id: int = None,
        type: Optional[AdType] = None,
        sort: Optional[SortOrder] = SortOrder.NEWEST,
        session: AsyncSession = Depends(get_db),
):
    return await get_ads(limit, offset, category_id, type, sort, session)


@router.delete("/{ad_id}")
async def delete_ad_endpoint(
        ad_id: int,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete_ad(ad_id=ad_id, session=session, current_user=current_user)


@router.post("/delete-many")
async def delete_ads_endpoint(
        data: list[AdDelete],
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await delete_ads([name.id for name in data], session, current_user)


@router.patch("/{ad_id}")
async def update_ad_endpoint(
        ad_id: int,
        data: AdUpdate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return await edit_ad(ad_id, data, session, current_user)


@router.post("/{ad_id}/image")
async def upload_photo_to_ad_endpoint(
        ad_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await upload_image(ad_id, file, current_user, session)

async def send_notification():
    pass
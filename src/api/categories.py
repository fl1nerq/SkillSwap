from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.models import Category
from src.schemas.schemas import CategoriesCreate
from src.services.categories import get_categories, create_categories

router = APIRouter(prefix="/categories", tags=["category"])


@router.get("/")
async def get_categories_endpoint(response: Response, session: AsyncSession = Depends(get_db)):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return await get_categories(session)


@router.post("/create")
async def create_categories_endpoint(data: CategoriesCreate, session: AsyncSession = Depends(get_db)):
    await create_categories(data, session)

    return {"message": "Categories created successfully"}

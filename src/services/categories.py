from fastapi import HTTPException

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from src.database import get_db
from src.models.models import Category
from src.schemas.schemas import CategoriesCreate


async def get_categories(session: AsyncSession):

    stmt = select(Category)
    result = await session.execute(stmt)
    return result.scalars().all()



async def create_categories(data: CategoriesCreate, session: AsyncSession):
    stmt = select(Category.name)
    result = await session.execute(stmt)
    existing_categories = result.scalars().all()

    added_count = 0

    for new_name in data.names:
        if new_name not in existing_categories:
            new_category = Category(name=new_name)
            session.add(new_category)
            existing_categories.append(new_name)
            added_count += 1

    if added_count > 0:
        await session.commit()

    return {"message": f"Successfully added {added_count} new categories"}



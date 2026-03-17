from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import get_password_hash, verify_password
from src.models.models import User, UserRole
from src.schemas.schemas import UserCreate


async def create_new_user(session: AsyncSession, user_in: UserCreate) -> User:
    stmt = select(User).where(
        or_(User.email == user_in.email, User.username == user_in.username)
    )
    result = await session.execute(stmt)

    existing_user = result.scalars().first()
    if existing_user:
        if existing_user.email == user_in.email:
            raise ValueError("Email already exists")
        else:
            raise ValueError("Username already taken")

    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        bio=user_in.bio,
        location=user_in.location,
        role=UserRole.USER
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def authenticate_user(session: AsyncSession, email:str, password:str) -> User:

    stmt = select(User).where(User.email==email)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

async def get_user_by_id(session:AsyncSession, user_id:int) -> User:

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    return user


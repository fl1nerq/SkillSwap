from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED
from fastapi.security import OAuth2PasswordRequestForm
from src.services.users import authenticate_user
from src.auth.security import create_access_token
from src.schemas.schemas import UserCreate, UserRead
from src.database import get_db
from src.services.users import create_new_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_db)):
    try:
        new_user = await create_new_user(session=session, user_in=user_in)
        return new_user

    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", status_code=HTTP_202_ACCEPTED)
async def login_for_access_token(
        data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(session, email=data.username, password=data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

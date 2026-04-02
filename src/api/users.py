from fastapi import APIRouter
from fastapi.params import Depends

from src.auth.security import get_current_user
from src.schemas.schemas import UserRead
from src.models.models import User

router = APIRouter(prefix="/users", tags=["user"])

@router.get("/me", response_model=UserRead)
async def get_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

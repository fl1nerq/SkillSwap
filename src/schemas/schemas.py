from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime

from fastapi.params import Query

from src.models.models import UserRole, AdType, DealStatus


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(max_length=72)
    bio: Optional[str] = None
    location: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    bio: Optional[str]
    location: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoriesRead(BaseModel):
    name: str


class CategoriesCreate(BaseModel):
    names: list[str]


class AdCreate(BaseModel):
    title: str
    description: str
    type: AdType
    category_id: int


class AdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: int
    title: str
    description: str
    type: AdType
    created_at: datetime


class UserShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str


class CategoryShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class AdReadFull(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: UserShort
    category: CategoryShort
    title: str
    description: str
    type: AdType
    created_at: datetime


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AdType] = None
    category_id: Optional[int]= None


class AdDelete(BaseModel):
    id: int


class AdShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class DealCreate(BaseModel):
    ad_id: int


class DealRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    initiator_id: int
    status: DealStatus
    created_at: datetime
    ad_id: int
    receiver_id: int



class DealReadFull(DealRead):
    user_initiated_by: UserShort
    ad: AdShort


class MessageCreate(BaseModel):
    content: str

class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime


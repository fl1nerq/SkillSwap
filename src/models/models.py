import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Enum, Text, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.database import Model


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class AdType(str, enum.Enum):
    OFFER = 'offer'
    REQUEST = 'request'


class DealStatus(str, enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class SortOrder(str, enum.Enum):
    NEWEST = "newest"
    OLDEST = "oldest"


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), default=UserRole.USER)
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    ads: Mapped[List["Ad"]] = relationship(back_populates="user")
    initiated: Mapped[List["Deal"]] = relationship(back_populates="user_initiated_by",
                                                   foreign_keys="[Deal.initiator_id]")
    received: Mapped[List["Deal"]] = relationship(back_populates="user_received_by", foreign_keys="[Deal.receiver_id]")
    user_messages: Mapped[List["Message"]] = relationship(back_populates="message_sender")
    user_reviews: Mapped[List["Review"]] = relationship(back_populates="review_sender")


class Category(Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    ads_category: Mapped[List["Ad"]] = relationship(back_populates="category")


class Ad(Model):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[AdType] = mapped_column(Enum(AdType, name="ad_type_enum"), default=AdType.OFFER)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    image_url: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="ads")
    category: Mapped["Category"] = relationship(back_populates="ads_category")

    deals: Mapped[List["Deal"]] = relationship(back_populates="ad")


class Deal(Model):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    ad_id: Mapped[int] = mapped_column(ForeignKey("ads.id", ondelete="CASCADE"))
    initiator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus, name="deal_status_enum"), default=DealStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_initiated_by: Mapped["User"] = relationship(foreign_keys=[initiator_id], back_populates="initiated")
    user_received_by: Mapped["User"] = relationship(foreign_keys=[receiver_id], back_populates="received")
    ad: Mapped["Ad"] = relationship(back_populates="deals")
    messages: Mapped[List["Message"]] = relationship(back_populates="message_deal")

    reviews: Mapped[List["Review"]] = relationship(back_populates="review_deal")


class Message(Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    message_deal: Mapped["Deal"] = relationship(back_populates="messages")
    message_sender: Mapped["User"] = relationship(back_populates="user_messages")


class Review(Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(CheckConstraint("rating >= 1 AND rating <= 5"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    review_deal: Mapped["Deal"] = relationship(back_populates="reviews")
    review_sender: Mapped["User"] = relationship(back_populates="user_reviews")

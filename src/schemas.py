from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    email: str
    password: str


class User(UserBase):
    id: int
    subscriptions: List["Subscription"] = []

    class Config:
        orm_mode: True


class MagazineBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float


class MagazineCreate(MagazineBase):
    name: str
    description: str
    base_price: float


class Magazine(MagazineBase):
    id: int
    subscriptions: List["Subscription"] = []

    class Config:
        orm_mode: True


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    renewal_period: int
    tier: int
    discount: float


class PlanCreate(PlanBase):
    title: str
    description: str
    renewal_period: int
    tier: int
    discount: float


class Plan(PlanBase):
    id: int
    subscriptions: List["Subscription"] = []

    class Config:
        orm_mode: True


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: date
    price: float
    is_active: bool = True


class SubscriptionCreate(SubscriptionBase):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: date


class Subscription(SubscriptionBase):
    id: int

    class Config:
        orm_mode: True

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
   
    subscriptions = relationship("Subscription", back_populates="user")

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)

    @staticmethod
    def hash_password(self, password: str) -> str:
        self.password = pwd_context.hash(password)


class Magazine(Base):
    __tablename__ = "magazines"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    base_price = Column(Float, nullable=False)

    subscriptions = relationship("Subscription", back_populates="magazine")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    renewal_period = Column(Integer, nullable=False)
    tier = Column(Integer, nullable=False)
    discount = Column(Float, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    renewal_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="subscriptions")
    magazine = relationship("Magazine", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

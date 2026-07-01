'''
Models for users
'''

from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    '''
    Class for users
    '''
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String(150))
    last_name = Column(String(150))
    password = Column(String)
    balance = Column(Integer, default=100)
    is_superuser = Column(Boolean, default=False)
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baskets = relationship("BiddingBasket", back_populates="user")

'''
Models for users
'''

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    '''
    Class for users
    '''
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String(150))
    last_name = Column(String(150))
    password = Column(String)
    balance = Column(Integer, default=0)
    is_superuser = Column(Boolean, default=0)
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="user")
    baskets = relationship("BiddingBasket", back_populates="user")

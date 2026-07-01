'''
Models for collections
'''

from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Collection(Base):
    '''
    class for collections
    '''
    __tablename__ = "collections"

    game_id = Column(BigInteger, primary_key=True, index=True)
    game_name = Column(String)
    game_status = Column(String)
    expires_at = Column(DateTime(timezone=True))
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # notes = relationship("Note", back_populates="collection")
    # user = relationship("User", back_populates="collections")
    baskets = relationship("BiddingBasket", back_populates="collection")

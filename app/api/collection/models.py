'''
Models for collections
'''

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Collection(Base):
    '''
    class for collections
    '''
    __tablename__ = "collections"

    game_id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String)
    game_status = Column(String)
    expires_at = Column(DateTime(timezone=True))
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baskets = relationship("BiddingBasket", back_populates="collection")

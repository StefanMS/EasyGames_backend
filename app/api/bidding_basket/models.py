'''
Models for collections
'''

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class BiddingBasket(Base):
    '''
    class for collections
    '''
    __tablename__ = "bidding_baskets"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(ForeignKey("collections.game_id"))
    player_id = Column(ForeignKey("users.id"))
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="baskets")
    collection = relationship("Collection", back_populates="baskets")

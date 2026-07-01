'''
Models for bidding basket
'''

from sqlalchemy import Column, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class BiddingBasket(Base):
    '''
    Class for bidding basket
    '''
    __tablename__ = "bidding_baskets"

    id = Column(BigInteger, primary_key=True, index=True)
    game_id = Column(BigInteger, ForeignKey("collections.game_id"))
    player_id = Column(BigInteger, ForeignKey("users.id"))
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="baskets")
    collection = relationship("Collection", back_populates="baskets")

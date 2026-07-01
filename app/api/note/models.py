'''
models for user notes
'''

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Note(Base):
    '''
    class for user notes
    '''
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    note = Column(String)
    user_id = Column(ForeignKey("users.id"))
    # pylint: disable=not-callable
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notes")

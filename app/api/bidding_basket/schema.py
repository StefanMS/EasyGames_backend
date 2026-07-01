from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class BiddingBasketSchema(BaseModel):
    game_id: int
    player_id: int

    class Config:
        orm_mode = True


class BiddingBasketCreate(BaseModel):
    pass


class BiddingBasketUpdate(BaseModel):
    game_id: Optional[int] = None


class BiddingBasketResponse(BaseModel):
    id: int
    game_id: int
    player_id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class BiddingBasket(BiddingBasketResponse):
    pass


class BiddingBasketUserFiltered(BaseModel):
    id: int
    game_name: str
    game_status: str
    enrolled_user: bool
    capacity: int
    countdown: Dict[str, str]
    image_url: str

    class Config:
        orm_mode = True

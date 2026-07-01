from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select
from app.api.collection.models import Collection
from app.api.bidding_basket.models import BiddingBasket
from app.api.collection.schema import CollectionCreate
from typing import Optional
from datetime import datetime


async def get_collection_by_user_id(db: AsyncSession,
                                    user_id: int) -> Optional[Collection]:
    result = await db.execute(
        select(Collection)
        .join(BiddingBasket, BiddingBasket.game_id == Collection.game_id)
        .filter(BiddingBasket.player_id == user_id)
    )
    return result.scalars().first()


async def create_game(db: AsyncSession, game: CollectionCreate) -> Collection:
    new_game = Collection(
        game_name=game.game_name,
        game_status=game.game_status,
        expires_at=game.expires_at
    )
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game


async def update_game_status(db: AsyncSession, 
                             game_id: int) -> Optional[Collection]:
    result = await db.execute(select(Collection).filter_by(game_id=game_id))
    collection = result.scalars().first()
    if collection:
        collection.game_status = "active" if \
                collection.game_status == "inactive" else "inactive"
        await db.commit()
        await db.refresh(collection)
    return collection


async def reset_game(db: AsyncSession, game_id: int) -> None:
    await db.execute(
        text("DELETE FROM bidding_baskets WHERE game_id = :game_id"),
        {"game_id": game_id}
    )
    await db.commit()


async def update_game_expiry(db: AsyncSession, game_id: int, 
                             new_expiry: datetime) -> Optional[Collection]:
    result = await db.execute(select(Collection).filter_by(game_id=game_id))
    collection = result.scalars().first()
    if collection:
        collection.expires_at = new_expiry
        await db.commit()
        await db.refresh(collection)
    return collection

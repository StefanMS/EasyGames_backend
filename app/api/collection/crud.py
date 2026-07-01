from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select
from app.api.collection.models import Collection
from app.api.collection.schema import CollectionCreate
from app.api.user.models import User
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException


async def get_collection_by_game_id(db: AsyncSession,
                                    game_id: int) -> Collection:
    result = await db.execute(select(Collection).filter(
        Collection.game_id == game_id))
    return result.scalars().first()


async def get_all_collections(db: AsyncSession,
                              skip: int = 0,
                              limit: int = 10) -> List[Collection]:
    result = await db.execute(select(Collection).offset(skip).limit(limit))
    return result.scalars().all()


async def create_game(db: AsyncSession,
                      game: CollectionCreate,
                      current_user: User) -> Collection:
    if current_user.is_superuser:
        new_game = Collection(
            game_name=game.game_name,
            game_status=game.game_status,
            expires_at=game.expires_at
        )
        db.add(new_game)
        await db.commit()
        await db.refresh(new_game)
        return new_game
    else:
        raise HTTPException(status_code=403,
                            detail="Not authorized to create games")


async def update_game_status(db: AsyncSession,
                             game_id: int,
                             current_user: User) -> Optional[Collection]:
    if current_user.is_superuser:
        result = await db.execute(select(Collection).filter(
                                        Collection.game_id == game_id))
        collection = result.scalars().first()
        if collection:
            collection.game_status = "active" if \
                    collection.game_status == "inactive" else "inactive"

            await db.commit()
            await db.refresh(collection)
            return collection
        else:
            return None
    else:
        raise HTTPException(status_code=403,
                            detail="Not authorized to update games")


async def update_game_expiry(db: AsyncSession,
                             game_id: int,
                             new_expiry: datetime,
                             current_user: User) -> Optional[Collection]:
    if current_user.is_superuser:
        result = await db.execute(select(Collection).filter(
                                        Collection.game_id == game_id))
        collection = result.scalars().first()
        if collection:
            collection.expires_at = new_expiry
            await db.commit()
            await db.refresh(collection)
            return collection
        else:
            return None
    else:
        raise HTTPException(status_code=403,
                            detail="Not authorized to update games")


async def delete_game(db: AsyncSession,
                      game_id: int,
                      current_user: User) -> Optional[Collection]:
    """
    Deletes a game (collection) from the database.
    Only accessible by superusers.
    """
    if current_user.is_superuser:
        result = await db.execute(select(Collection).filter(
                                        Collection.game_id == game_id))
        collection = result.scalars().first()

        if collection:
            await db.delete(collection)
            await db.commit()
            return collection
        else:
            return None
    else:
        raise HTTPException(status_code=403,
                            detail="Not authorized to delete games")

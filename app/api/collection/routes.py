from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.api.collection.crud import (
    get_collection_by_user_id,
    create_game,
    update_game_status,
    reset_game,
    update_game_expiry,
)
from app.api.collection.schema import CollectionCreate, CollectionResponse
from app.db.session import get_db

router = APIRouter()


@router.get("/collections/{user_id}",
            response_model=Optional[CollectionResponse])
async def get_collection(user_id: int, db: AsyncSession = Depends(get_db)):
    collection = await get_collection_by_user_id(db, user_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.post("/add-game", response_model=CollectionResponse)
async def add_game(
    game_name: str = Form(...),
    active_game: bool = Form(False),
    expires_at: Optional[datetime] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    game_status = 'active' if active_game else 'inactive'
    game_data = CollectionCreate(game_name=game_name,
                                 game_status=game_status,
                                 expires_at=expires_at)
    new_game = await create_game(db, game_data)
    return new_game


@router.post("/activate-game/{game_id}",
             response_model=Optional[CollectionResponse])
async def activate_game(game_id: int, db: AsyncSession = Depends(get_db)):
    collection = await update_game_status(db, game_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Game not found")
    return collection


@router.post("/reset-game/{game_id}")
async def reset_game_route(game_id: int, db: AsyncSession = Depends(get_db)):
    await reset_game(db, game_id)
    return {"detail": "Game reset successful"}


@router.post("/update-expiry/{game_id}",
             response_model=Optional[CollectionResponse])
async def update_game_expiry_route(
    game_id: int,
    new_expiry: datetime,
    db: AsyncSession = Depends(get_db),
):
    collection = await update_game_expiry(db, game_id, new_expiry)
    if not collection:
        raise HTTPException(status_code=404, detail="Game not found")
    return collection

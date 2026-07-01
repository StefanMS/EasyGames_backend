from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from app.api.bidding_basket.crud import (
    create_bid,
    get_all_bidding_baskets,
    get_bidding_basket_by_id,
    user_filtered_collection,
    update_bid,
    delete_bid
)
from app.db.session import get_db, get_current_user
from app.api.bidding_basket.schema import BiddingBasket, BiddingBasketUpdate
from app.api.collection.models import Collection

router = APIRouter()


@router.post("/bids/", response_model=BiddingBasket)
async def create_bid_route(
    game_id: int,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bid for a game by the current user.
    """
    new_bid = await create_bid(db=db, game_id=game_id, player_id=current_user)
    return new_bid


@router.put("/bids/{bid_id}", response_model=BiddingBasket)
async def update_bid_route(
    bid_id: int,
    bid_update: BiddingBasketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Update a bid by its ID.
    """
    bid = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bidding basket not found")

    # Ensure the current user is the owner of the bid
    if bid.player_id != current_user:
        raise HTTPException(status_code=403,
                            detail="Not authorized to update this bid")

    updates = bid_update.model_dump(exclude_unset=True)
    updated_bid = await update_bid(db=db, bid_id=bid_id, **updates)
    return updated_bid


@router.delete("/bids/{bid_id}", response_model=Dict[str, Any])
async def delete_bid_route(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Delete a bid by its ID.
    """
    bid = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bidding basket not found")

    # Ensure the current user is the owner of the bid
    if bid.player_id != current_user:
        raise HTTPException(status_code=403,
                            detail="Not authorized to delete this bid")

    success = await delete_bid(db=db, bid_id=bid_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete bid")

    return {"detail": "Bid deleted successfully"}


@router.get("/bids/", response_model=List[BiddingBasket])
async def get_all_bidding_baskets_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all bidding baskets with pagination.
    """
    return await get_all_bidding_baskets(db=db, skip=skip, limit=limit)


@router.get("/bids/{bid_id}", response_model=Optional[BiddingBasket])
async def get_bidding_basket_by_id_route(
    bid_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a bidding basket by its ID.
    """
    bidding_basket = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bidding_basket:
        raise HTTPException(status_code=404, detail="Bidding basket not found")
    return bidding_basket


@router.get("/user-collections/", response_model=List[Dict[str, Any]])
async def get_user_filtered_collections_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Get a list of active games filtered and formatted for the current user,
    with pagination.
    """
    # Fetch active games (replace with your actual query logic)
    active_games = await db.execute(select(Collection).filter_by(
        game_status="active"))
    active_games_list = active_games.scalars().all()

    filtered_collection = await user_filtered_collection(db,
                                                         active_games_list,
                                                         current_user,
                                                         skip=skip,
                                                         limit=limit)

    return filtered_collection

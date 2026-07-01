from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
from app.api.bidding_basket.schema import BiddingBasketUserFiltered
from app.api.bidding_basket.crud import (
    create_bid,
    get_all_bidding_baskets,
    get_bidding_basket_by_id,
    user_filtered_collection,
    update_bid,
    delete_bid
)
from app.core.auth import get_current_user
from app.db.session import get_db
from app.api.bidding_basket.schema import (
    BiddingBasketCreate,
    BiddingBasketResponse)
from app.api.collection.models import Collection
from app.api.user.models import User

router = APIRouter()


@router.post("/bids/", response_model=BiddingBasketCreate,
             tags=["Bidding Basket"])
async def create_bid_route(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_bid = await create_bid(db=db,
                               game_id=game_id,
                               current_user=current_user)
    return new_bid


@router.put("/bids/{bid_id}", response_model=BiddingBasketResponse,
            tags=["Bidding Basket"])
async def update_bid_route(
    bid_id: int,
    bid_update: BiddingBasketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    **kwargs: Dict[str, Any]
):
    bid = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bid:
        raise HTTPException(status_code=404,
                            detail="Bidding basket not found")

    if bid.player_id != current_user.id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to update this bid")

    updates = bid_update.model_dump(exclude_unset=True)
    updated_bid = await update_bid(db=db, bid_id=bid_id, **updates)
    return updated_bid


@router.delete("/bids/{bid_id}", response_model=BiddingBasketResponse,
               tags=["Bidding Basket"])
async def delete_bid_route(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bid = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bid:
        raise HTTPException(status_code=404,
                            detail="Bidding basket not found")

    if bid.player_id != current_user.id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to delete this bid")

    success = await delete_bid(db=db, bid_id=bid_id)
    if not success:
        raise HTTPException(status_code=400,
                            detail="Failed to delete bid")

    return {"detail": "Bid deleted successfully"}


@router.get("/bids/", response_model=List[BiddingBasketResponse],
            tags=["Bidding Basket"])
async def get_all_bidding_baskets_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await get_all_bidding_baskets(db=db, skip=skip, limit=limit)


@router.get("/bids/{bid_id}", response_model=Optional[BiddingBasketResponse],
            tags=["Bidding Basket"])
async def get_bidding_basket_by_id_route(
    bid_id: int,
    db: AsyncSession = Depends(get_db)
):
    bidding_basket = await get_bidding_basket_by_id(db=db, bid_id=bid_id)
    if not bidding_basket:
        raise HTTPException(status_code=404,
                            detail="Bidding basket not found")
    return bidding_basket


@router.get("/user-collections/",
            response_model=List[BiddingBasketUserFiltered],
            tags=["Bidding Basket"])
async def get_user_filtered_collections_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_games = await db.execute(select(Collection).filter(
           Collection.game_status == "active"))
    active_games_list = active_games.scalars().all()

    filtered_collection = await user_filtered_collection(db,
                                                         active_games_list,
                                                         current_user,
                                                         skip=skip,
                                                         limit=limit)

    return filtered_collection

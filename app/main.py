'''
Main module for backend development of EasyGames
'''

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from .api.user.routes import router as user_router
from .api.collection.routes import router as collection_router
from .api.bidding_basket.routes import router as bidding_basket_router
from app.db.initialize import create_superuser
from app.db.session import engine
from app.api.user.models import Base as UserBase
from app.api.bidding_basket.models import Base as BiddingBasketBase
from app.api.collection.models import Base as CollectionBase


load_dotenv(override=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(BiddingBasketBase.metadata.create_all)
        await conn.run_sync(CollectionBase.metadata.create_all)

    await create_superuser()
    yield

app = FastAPI(title="Backend for EasyGames",
              version="0.0.1",
              lifespan=lifespan)

app.include_router(user_router)
app.include_router(collection_router)
app.include_router(bidding_basket_router)

# CORS middleware
origins = [
    f"{os.getenv('API_URL')}",
    "http://localhost:3000",
]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

'''
Main module for backend development of EasyGames
'''

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.user.routes import router as user_router
from .api.collection.routes import router as collection_router
from .api.bidding_basket.routes import router as bidding_basket_router
from .api.note.routes import router as notes_router
from .db.base import Base
from .db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(collection_router)
app.include_router(bidding_basket_router)
app.include_router(notes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

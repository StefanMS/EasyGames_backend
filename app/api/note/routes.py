from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.note import crud
from app.api.note.schema import NoteCreate, NoteUpdate, NoteResponse
from app.db.session import get_db, get_current_user

router = APIRouter()


@router.post("/notes/", response_model=NoteResponse)
async def create_note_route(note: NoteCreate,
                            db: AsyncSession = Depends(get_db)):
    return await crud.create_note(db=db, note=note)


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note_route(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await crud.get_note_by_id(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/notes/", response_model=List[NoteResponse])
async def get_notes_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return await crud.get_notes_by_user_id(db=db, user_id=current_user,
                                           skip=skip, limit=limit)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note_route(
    note_id: int,
    note_update: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    note = await crud.get_note_by_id(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user:
        raise HTTPException(status_code=403,
                            detail="Not authorized to update this note")

    updated_note = await crud.update_note(db=db, note_id=note_id,
                                          note_update=note_update)
    return updated_note


@router.delete("/notes/{note_id}")
async def delete_note_route(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    note = await crud.get_note_by_id(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != current_user:
        raise HTTPException(status_code=403,
                            detail="Not authorized to delete this note")

    success = await crud.delete_note(db=db, note_id=note_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete note")
    return {"detail": "Note deleted successfully"}

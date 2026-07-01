from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.note.models import Note
from app.api.note.schema import NoteCreate, NoteUpdate


async def create_note(db: AsyncSession, note: NoteCreate) -> Note:
    new_note = Note(note=note.note, user_id=note.user_id)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


async def get_note_by_id(db: AsyncSession, note_id: int) -> Optional[Note]:
    result = await db.execute(select(Note).filter(Note.id == note_id))
    return result.scalars().first()


async def get_notes_by_user_id(db: AsyncSession, user_id: int,
                               skip: int = 0, limit: int = 10) -> List[Note]:
    result = await db.execute(
        select(Note).filter(Note.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_note(db: AsyncSession, note_id: int,
                      note_update: NoteUpdate) -> Optional[Note]:
    note = await get_note_by_id(db, note_id)
    if not note:
        return None

    for key, value in note_update.model_dump(exclude_unset=True).items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, note_id: int) -> bool:
    note = await get_note_by_id(db, note_id)
    if not note:
        return False

    await db.delete(note)
    await db.commit()
    return True

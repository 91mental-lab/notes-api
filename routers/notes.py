from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.Note)
def create_note_for_current_user(
    note: schemas.NoteCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_user_note(db=db, note=note, user_id=current_user.id)

@router.get("/", response_model=list[schemas.Note])
def read_user_notes(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(db, user_id=current_user.id, skip=skip, limit=limit)
    return notes

@router.get("/{note_id}", response_model=schemas.Note)
def read_note_by_id(
    note_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this note")
    return note

@router.put("/{note_id}", response_model=schemas.Note)
def update_note_by_id(
    note_id: int,
    note_update: schemas.NoteUpdate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if db_note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")
    return crud.update_note(db=db, note=note_update, db_note=db_note)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_by_id(
    note_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if db_note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    crud.delete_note(db=db, db_note=db_note)
    return
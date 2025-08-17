from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import auth, crud, schemas
from ..errors.models import ErrorResponse
from typing import List

router = APIRouter()

@router.post("/",
             response_model=schemas.Note,
             status_code=status.HTTP_201_CREATED, # Статус 201 Created для успешного создания
             summary="Create a new note for the current user",
             responses={
                 # Документируем ошибку 401 Unauthorized (если пользователь не аутентифицирован)
                 status.HTTP_401_UNAUTHORIZED: {
                     "model": ErrorResponse,
                     "description": "Not authenticated or token expired/invalid."
                 },
                 # Документируем ошибку валидации Pydantic (статус 422)
                 status.HTTP_422_UNPROCESSABLE_ENTITY: {
                     "model": ErrorResponse,
                     "description": "Validation error for input data."
                 }
             })
def create_note_for_current_user(
    note: schemas.NoteCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_user_note(db=db, note=note, user_id=current_user.id)


@router.get("/",
            response_model=List[schemas.Note],  # Используем List[schemas.Note] для списка
            summary="Get all notes for the current user",
            responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "model": ErrorResponse,
                     "description": "Not authenticated or token expired/invalid."
                 }
             })
def read_user_notes(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(db, user_id=current_user.id, skip=skip, limit=limit)
    return notes


@router.get("/{note_id}",
             response_model=schemas.Note,
             summary="Get a specific note by ID",
             responses={
                 status.HTTP_401_UNAUTHORIZED: {
                     "model": ErrorResponse,
                     "description": "Not authenticated or token expired/invalid."
                 },
                 status.HTTP_403_FORBIDDEN: {
                     "model": ErrorResponse,
                     "description": "Not authorized to view this note."
                 },
                 status.HTTP_404_NOT_FOUND: {
                     "model": ErrorResponse,
                     "description": "Note not found."
                 }
             })
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


@router.put("/{note_id}",
            response_model=schemas.Note,
            summary="Update an existing note by ID",
            responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "model": ErrorResponse,
                    "description": "Not authenticated or token expired/invalid."
                },
                status.HTTP_403_FORBIDDEN: {
                    "model": ErrorResponse,
                    "description": "Not authorized to update this note."
                },
                status.HTTP_404_NOT_FOUND: {
                    "model": ErrorResponse,
                    "description": "Note not found."
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": ErrorResponse,
                    "description": "Validation error for input data."
                }
            })
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


@router.delete("/{note_id}",
                status_code=status.HTTP_204_NO_CONTENT, # Статус 204 No Content для успешного удаления
                summary="Delete a note by ID",
                responses={
                    status.HTTP_401_UNAUTHORIZED: {
                        "model": ErrorResponse,
                        "description": "Not authenticated or token expired/invalid."
                    },
                    status.HTTP_403_FORBIDDEN: {
                        "model": ErrorResponse,
                        "description": "Not authorized to delete this note."
                    },
                    status.HTTP_404_NOT_FOUND: {
                        "model": ErrorResponse,
                        "description": "Note not found."
                    }
                })
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
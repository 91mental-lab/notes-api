from sqlalchemy.orm import Session
from .models import User, Note
from .schemas import UserCreate, NoteCreate, NoteUpdate
from .auth import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Note).filter(Note.owner_id == user_id).offset(skip).limit(limit).all()


def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def create_user_note(db: Session, note: NoteCreate, user_id: int):
    db_note = Note(**note.model_dump(), owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note: NoteUpdate, db_note: Note):
    for key, value in note.model_dump(exclude_unset=True).items():
        setattr(db_note, key, value)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, db_note: Note):
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}
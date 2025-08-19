from fastapi import FastAPI

# Импорт обработчиков ошибок
from .errors.handlers import register_exception_handlers

# --- Исправляем импорты ---
# Теперь все импорты должны начинаться с SecureNotesAPI.
from .database import engine, Base, get_db # <--- ИСПРАВЛЕНО: добавлено SecureNotesAPI.
from .routers import users, notes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Personal Notes API",
    description="A simple API for managing personal notes with user authentication."
)


register_exception_handlers(app)


@app.get("/")
async def read_root():
    return {"message": "Welcome to Secure Personal Notes API!"}

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
from fastapi import FastAPI
from database import engine, Base
from routers import users, notes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Personal Notes API",
    description="A simple API for managing personal notes with user authentication."
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Secure Personal Notes API!"}

# Добавляем роутеры (после их создания)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
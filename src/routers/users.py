from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from .. import auth, crud, schemas
from ..errors.models import UserAlreadyExistsError, ErrorResponse
from typing import Dict

router = APIRouter()

@router.post("/",
             response_model=schemas.User,
             status_code=status.HTTP_201_CREATED, # Статус 201 Created для успешного создания
             summary="Create a new user account",
             responses={
                 # Документируем ошибку, которую поймает UserAlreadyExistsError handler (статус 409)
                 status.HTTP_409_CONFLICT: {
                     "model": ErrorResponse,
                     "description": "Username or email already registered."
                 },
                 # Документируем ошибку валидации Pydantic (статус 422)
                 status.HTTP_422_UNPROCESSABLE_ENTITY: {
                     "model": ErrorResponse,
                     "description": "Validation error for input data."
                 }
             })
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise UserAlreadyExistsError(username=user.username)
    return crud.create_user(db=db, user=user)


@router.post("/token",
             response_model=Dict[str, str], # Указываем тип возвращаемого значения для ответа
             summary="Authenticate user and get an access token",
             responses={
                 # Документируем ошибку 401 Unauthorized
                 status.HTTP_401_UNAUTHORIZED: {
                     "model": ErrorResponse,
                     "description": "Incorrect username or password / Invalid authentication credentials."
                 }
             })
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/",
             response_model=schemas.User,
             summary="Get details of the current authenticated user",
             responses={
                 # Документируем ошибку 401 Unauthorized
                 status.HTTP_401_UNAUTHORIZED: {
                     "model": ErrorResponse,
                     "description": "Not authenticated or token expired/invalid."
                 },
                 # Если get_current_user может возвращать 403 Forbidden (например, для неактивных пользователей)
                 status.HTTP_403_FORBIDDEN: {
                     "model": ErrorResponse,
                     "description": "Not authorized to access this resource (e.g., inactive user)."
                 }
             })
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user
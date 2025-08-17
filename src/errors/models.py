from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class UserAlreadyExistsError(Exception):
    def __init__(self, username: str):
        self.username = username
        self.message = f"User with username '{username}' already exists."


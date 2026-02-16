from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    full_name: str
    email: str
    password_hash: str

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: UUID
    full_name: str
    email: str
    password_hash: str

    # model_config = ConfigDict(from_attributes=True)

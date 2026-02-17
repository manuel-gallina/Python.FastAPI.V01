from uuid import UUID

from api.shared.models import BaseDbModel


class User(BaseDbModel):
    id: UUID
    full_name: str
    email: str
    password_hash: str

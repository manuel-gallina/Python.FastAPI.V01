"""init_database

Revision ID: fc7425fa20a0
Revises:
Create Date: 2026-02-13 14:22:42.049013

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fc7425fa20a0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("create schema auth;")
    op.execute("""
               create table python_fastapi_v01.auth.user
               (
                   id        uuid,
                   full_name varchar not null,
                   email     varchar not null,
                   password_hash varchar not null,
                   constraint u__id__pk primary key (id),
                   constraint u__email__uk unique (email),
                   constraint u_password_hash__uk unique (password_hash)
               );
               """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop schema auth;")

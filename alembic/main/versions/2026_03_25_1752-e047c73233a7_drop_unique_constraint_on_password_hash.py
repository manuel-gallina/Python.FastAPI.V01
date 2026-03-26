"""drop_unique_constraint_on_password_hash

Revision ID: e047c73233a7
Revises: fc7425fa20a0
Create Date: 2026-03-25 17:52:47.113200

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e047c73233a7"
down_revision: Union[str, Sequence[str], None] = "fc7425fa20a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "alter table auth.user drop constraint if exists u_password_hash__uk;"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "alter table auth.user add constraint u_password_hash__uk unique (password_hash);"
    )

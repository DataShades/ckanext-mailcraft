"""Add mailcraft_mail table.

Revision ID: 9f83e5bfff72
Revises:
Create Date: 2023-09-14 11:53:58.371935

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9f83e5bfff72"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mailcraft_mail",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("subject", sa.Text),
        sa.Column(
            "timestamp",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("sender", sa.Text),
        sa.Column("recipient", sa.Text),
        sa.Column("message", sa.Text),
        sa.Column("state", sa.Text, server_default="success"),
        sa.Column("extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade():
    op.drop_table("mailcraft_mail")

"""auto

Revision ID: a49b497248e1
Revises: 
Create Date: 2024-03-21 13:07:49.091355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a49b497248e1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False),
        sa.Column("visits", sa.Integer(), nullable=False),
        sa.Column(
            "last_visit_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_urls_original_url"), "urls", ["original_url"], unique=False
    )
    op.create_index(op.f("ix_urls_slug"), "urls", ["slug"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_urls_slug"), table_name="urls")
    op.drop_index(op.f("ix_urls_original_url"), table_name="urls")
    op.drop_table("urls")
    # ### end Alembic commands ###
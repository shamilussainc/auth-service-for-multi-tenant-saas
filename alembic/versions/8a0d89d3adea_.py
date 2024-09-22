"""empty message

Revision ID: 8a0d89d3adea
Revises: 457736ebe535
Create Date: 2024-09-22 19:14:43.143866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a0d89d3adea'
down_revision: Union[str, None] = '457736ebe535'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_user_invitations_token'),
                    'user_invitations', ['token'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_invitations_token'),
                  table_name='user_invitations')
    # ### end Alembic commands ###

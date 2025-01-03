"""initial

Revision ID: 1b4be1367e28
Revises: 
Create Date: 2024-11-07 15:47:10.003056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4be1367e28'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('platforms',
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('last_time_mark', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('telegram_id', sa.Integer(), nullable=False),
    sa.Column('utc_offset_minutes', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('filters',
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('filter_type', sa.Enum('KEYWORD', 'REGEX', 'VIEWS', 'RESPONSES', 'PRICE', 'LIFETIME', name='filtertype'), nullable=False),
    sa.Column('is_negative', sa.Boolean(), nullable=False),
    sa.Column('case_sensitive', sa.Boolean(), nullable=True),
    sa.Column('keyword', sa.Text(), nullable=True),
    sa.Column('regex', sa.Text(), nullable=True),
    sa.Column('min_views', sa.Integer(), nullable=True),
    sa.Column('max_views', sa.Integer(), nullable=True),
    sa.Column('min_responses', sa.Integer(), nullable=True),
    sa.Column('max_responses', sa.Integer(), nullable=True),
    sa.Column('price_type', sa.Enum('UNDEFINED', 'PER_PROJECT', 'PER_HOUR', name='pricetype'), nullable=True),
    sa.Column('min_price', sa.Integer(), nullable=True),
    sa.Column('max_price', sa.Integer(), nullable=True),
    sa.Column('min_lifetime_seconds', sa.Integer(), nullable=True),
    sa.Column('max_lifetime_seconds', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_disabled_platforms',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'platform_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_disabled_platforms')
    op.drop_table('filters')
    op.drop_table('users')
    op.drop_table('platforms')
    # ### end Alembic commands ###

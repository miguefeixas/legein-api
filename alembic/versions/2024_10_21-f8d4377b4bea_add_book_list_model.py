"""Add book list model

Revision ID: f8d4377b4bea
Revises: 4ce58f56b479
Create Date: 2024-10-21 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f8d4377b4bea'
down_revision: Union[str, None] = '4ce58f56b479'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'book_list',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('disabled', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('disabled_at', sa.DateTime(), nullable=True),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('disabled_by', sa.Integer(), nullable=True),
        sa.Column('modified_by', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], name='fk_created_by'),
        sa.ForeignKeyConstraint(['disabled_by'], ['user.id'], name='fk_disabled_by'),
        sa.ForeignKeyConstraint(['modified_by'], ['user.id'], name='fk_modified_by'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_book_list_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'book_list_book',
        sa.Column('book_list_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['book.id'], name='fk_book_list_book_book_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['book_list_id'],
            ['book_list.id'],
            name='fk_book_list_book_list_id',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('book_list_id', 'book_id'),
    )


def downgrade() -> None:
    op.drop_table('book_list_book')
    op.drop_table('book_list')

"""empty message

Revision ID: 29d947619020
Revises: a73c5ce3cdd0
Create Date: 2022-10-17 14:36:45.244027

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '29d947619020'
down_revision = 'a73c5ce3cdd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('username', table_name='user')
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', mysql.VARCHAR(length=120), nullable=False))
    op.add_column('user', sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.create_index('username', 'user', ['username'], unique=False)
    # ### end Alembic commands ###

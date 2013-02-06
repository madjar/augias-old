"""Inscription date for users

Revision ID: f026249530
Revises: 243d3039806
Create Date: 2013-01-29 21:56:01.016370

"""

# revision identifiers, used by Alembic.
revision = 'f026249530'
down_revision = '243d3039806'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('inscription_date', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'inscription_date')
    ### end Alembic commands ###
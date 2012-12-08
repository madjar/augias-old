"""Remove Task.length

Revision ID: 3441db8b467
Revises: None
Create Date: 2012-12-02 20:23:14.136565

"""

# revision identifiers, used by Alembic.
revision = '3441db8b467'
down_revision = None

import alembic, logging
from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    if type(op._proxy.impl) != alembic.ddl.sqlite.SQLiteImpl:
        op.drop_column('tasks', 'length')
    else:
        logging.warning('Can remove column in sqlite, so dirty hack')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    if type(op._proxy.impl) != alembic.ddl.sqlite.SQLiteImpl:
        op.add_column('tasks', sa.Column('length', sa.INTEGER(), nullable=True))
    ### end Alembic commands ###
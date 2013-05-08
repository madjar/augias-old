"""Added Invite.by

Revision ID: 18fece0d673
Revises: None
Create Date: 2013-05-08 16:27:00.212667

"""

# revision identifiers, used by Alembic.
revision = '18fece0d673'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('invites', sa.Column('by_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('invites', 'by_id')

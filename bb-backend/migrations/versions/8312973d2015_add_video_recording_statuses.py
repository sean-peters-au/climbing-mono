"""add video recordings

Revision ID: 8312973d2015
Revises: 307af79213b0
Create Date: 2024-11-26 12:42:31.457633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8312973d2015'
down_revision: Union[str, None] = '307af79213b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the enum type first
    op.execute("CREATE TYPE recording_status AS ENUM ('recording', 'completed', 'failed')")
    
    # Then use it in the table
    op.add_column('recordings', sa.Column('status', sa.Enum('recording', 'completed', 'failed', name='recording_status'), nullable=False, server_default='recording'))


def downgrade():
    op.drop_column('recordings', 'status')
    # Drop the enum type
    op.execute("DROP TYPE recording_status")

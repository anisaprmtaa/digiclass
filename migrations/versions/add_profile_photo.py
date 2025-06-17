"""add profile photo column

Revision ID: add_profile_photo
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_profile_photo'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add profile_photo column with default value
    op.add_column('user', sa.Column('profile_photo', sa.String(255), nullable=True, server_default='default.jpg'))

def downgrade():
    # Remove profile_photo column
    op.drop_column('user', 'profile_photo') 
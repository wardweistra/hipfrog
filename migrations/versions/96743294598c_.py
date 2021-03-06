"""empty message

Revision ID: 96743294598c
Revises: 679779987c7c
Create Date: 2016-07-14 22:15:08.472832

"""

# revision identifiers, used by Alembic.
revision = '96743294598c'
down_revision = '679779987c7c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('installations', sa.Column('access_token', sa.String(), nullable=True))
    op.add_column('installations', sa.Column('expires_in', sa.Integer(), nullable=True))
    op.add_column('installations', sa.Column('group_id', sa.Integer(), nullable=True))
    op.add_column('installations', sa.Column('group_name', sa.String(), nullable=True))
    op.add_column('installations', sa.Column('hipchatApiProvider_url', sa.String(), nullable=True))
    op.add_column('installations', sa.Column('scope', sa.String(), nullable=True))
    op.add_column('installations', sa.Column('token_type', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('installations', 'token_type')
    op.drop_column('installations', 'scope')
    op.drop_column('installations', 'hipchatApiProvider_url')
    op.drop_column('installations', 'group_name')
    op.drop_column('installations', 'group_id')
    op.drop_column('installations', 'expires_in')
    op.drop_column('installations', 'access_token')
    ### end Alembic commands ###

"""empty message

Revision ID: 59c105db2fc1
Revises: 74dbcfe556a8
Create Date: 2020-02-28 15:50:59.975713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59c105db2fc1'
down_revision = '74dbcfe556a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=True),
    sa.Column('state', sa.String(length=120), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.Column('website', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.String(length=120), nullable=False),
    sa.Column('seeking_talent', sa.Boolean(), nullable=False),
    sa.Column('upcoming_shows', sa.Integer(), nullable=False),
    sa.Column('past_shows', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('artist_name', sa.String(), nullable=False),
    sa.Column('artist_image_link', sa.String(length=500), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('venue_name', sa.String(), nullable=True),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['artist_image_link'], ['Artist.image_link'], ),
    sa.ForeignKeyConstraint(['artist_name'], ['Artist.name'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.ForeignKeyConstraint(['venue_name'], ['Venue.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('Artist', 'past_shows',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('Artist', 'upcoming_shows',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'upcoming_shows',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('Artist', 'past_shows',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('Show')
    op.drop_table('Venue')
    # ### end Alembic commands ###
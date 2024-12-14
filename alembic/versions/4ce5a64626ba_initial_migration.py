"""Initial migration

Revision ID: 4ce5a64626ba
Revises: 
Create Date: 2024-12-13 15:27:00.814962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ce5a64626ba'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mechanics',
    sa.Column('mechanic_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('login', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'MECHANIC', name='mechanicrole'), nullable=False),
    sa.Column('position', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('mechanic_id'),
    sa.UniqueConstraint('login')
    )
    op.create_index(op.f('ix_mechanics_mechanic_id'), 'mechanics', ['mechanic_id'], unique=False)
    op.create_table('services',
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('service_id')
    )
    op.create_index(op.f('ix_services_service_id'), 'services', ['service_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'CUSTOMER', name='userrole'), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('cars',
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('brand', sa.String(length=100), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('plate_number', sa.String(length=20), nullable=False),
    sa.Column('vin', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('car_id'),
    sa.UniqueConstraint('plate_number'),
    sa.UniqueConstraint('vin')
    )
    op.create_index(op.f('ix_cars_car_id'), 'cars', ['car_id'], unique=False)
    op.create_table('documents',
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('mechanic_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('PASSPORT', 'TAX_ID', 'DIPLOMA', 'EMPLOYMENT_CONTRACT', name='documenttype'), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['mechanic_id'], ['mechanics.mechanic_id'], ),
    sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index(op.f('ix_documents_document_id'), 'documents', ['document_id'], unique=False)
    op.create_table('appointments',
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('mechanic_id', sa.Integer(), nullable=True),
    sa.Column('appointment_date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', name='appointmentstatus'), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.car_id'], ),
    sa.ForeignKeyConstraint(['mechanic_id'], ['mechanics.mechanic_id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('appointment_id')
    )
    op.create_index(op.f('ix_appointments_appointment_id'), 'appointments', ['appointment_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_appointments_appointment_id'), table_name='appointments')
    op.drop_table('appointments')
    op.drop_index(op.f('ix_documents_document_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_cars_car_id'), table_name='cars')
    op.drop_table('cars')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_services_service_id'), table_name='services')
    op.drop_table('services')
    op.drop_index(op.f('ix_mechanics_mechanic_id'), table_name='mechanics')
    op.drop_table('mechanics')
    # ### end Alembic commands ###

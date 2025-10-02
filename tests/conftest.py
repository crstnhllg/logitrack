from app.core.security import bcrypt_context, get_current_user
from app.models import User, Vehicle, Order
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime
import pytest
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv('TEST_DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
client = TestClient(app)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope='function')
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    user = User(
        username='tintin',
        email='tintin@email.com',
        role='admin',
        hashed_password=bcrypt_context.hash('12345')
    )
    db_session.add(user)
    db_session.commit()
    yield user


@pytest.fixture
def test_vehicle(db_session):
    user = User(
        username='driver',
        email='driver@email.com',
        role='driver',
        hashed_password=bcrypt_context.hash('12345')
    )
    db_session.add(user)
    db_session.commit()

    vehicle = Vehicle(
        license_plate='12345abc',
        type='pickup',
        capacity_kg=750,
        status='available',
        driver_id=user.id
    )
    db_session.add(vehicle)
    db_session.commit()
    yield vehicle


@pytest.fixture
def test_order(db_session, test_vehicle):
    order = Order(
        destination='quezon city',
        size='m',
        priority=False,
        delivery_window_start=datetime(2025, 10, 2, 9, 0),
        delivery_window_end=datetime(2025, 10, 4, 18, 0),
        status='pending',
        vehicle_id=test_vehicle.id
    )
    db_session.add(order)
    db_session.commit()
    yield order


@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def override_current_user(test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
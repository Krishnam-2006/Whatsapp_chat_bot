import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = settings.test_database_url

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "Set TEST_DATABASE_URL to your test_recipebot PostgreSQL database URL."
    )

if "test_recipebot" not in TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL must point to the test_recipebot database.")

test_engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

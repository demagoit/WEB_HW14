import sys
import os
import pytest
import asyncio
import pytest_asyncio

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from src.database.models import Base
from src.database.db import get_db
from main import app

# SQLALCHEMY_DB_URL = 'sqlite:///./test.db'
# test_engine = create_engine(SQLALCHEMY_DB_URL, connect_args={'check_same_thread': False})
# TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=test_engine)

# SQLALCHEMY_DB_URL = 'sqlite+aiosqlite:///./test.db'
SQLALCHEMY_DB_URL = 'sqlite+aiosqlite:///:memory:'
test_engine = create_async_engine(SQLALCHEMY_DB_URL, connect_args={
                            'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = async_sessionmaker(
    autoflush=False, autocommit=False, expire_on_commit=False, bind=test_engine)


@pytest.fixture(scope='module', autouse=True)
def init_db():
    async def init_models():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init_models())

# @pytest.fixture(scope='module')
# def session():
#     Base.metadata.drop_all(bind=test_engine)
#     Base.metadata.create_all(bind=test_engine)

#     db = TestingSessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()

@pytest.fixture(scope='module')
def client():

    async def mock_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            await session.close()
        
    app.dependency_overrides[get_db] = mock_get_db

    yield TestClient(app=app)

@pytest.fixture(scope='function')
def mock_redis(monkeypatch):
    monkeypatch.setattr(
        "fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr(
        "fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr(
        "fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())


@pytest.fixture(scope='module')
def user():
    return {'username': 'test_user', 'email': 'user@test.com', 'password': 'secret78'}


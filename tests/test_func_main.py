from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from pytest import MonkeyPatch

import main


def test_root(monkeypatch: MonkeyPatch, mock_redis):
    # as a result of replacement of depricated @app.on_event('startup')
    # monkeypatch.setattr("fastapi_limiter.FastAPILimiter.init", AsyncMock())

    with TestClient(main.app) as client:
        responce = client.get('/')
        assert responce.status_code == 200
        assert responce.json() == {'message': 'Contacts application'}


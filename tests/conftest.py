import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'test.db'}"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["MODEL_AUTO_TRAIN"] = "true"

    from quadra_diag.core.config import get_settings
    from quadra_diag.services.prediction import load_bundle

    get_settings.cache_clear()
    load_bundle.cache_clear()

    from quadra_diag.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

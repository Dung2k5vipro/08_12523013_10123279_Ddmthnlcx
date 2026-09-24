import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure ai-models and service directories are in sys.path
service_dir = Path(__file__).resolve().parent.parent
ai_models_dir = service_dir.parent
if str(service_dir) not in sys.path:
    sys.path.insert(0, str(service_dir))
if str(ai_models_dir) not in sys.path:
    sys.path.insert(0, str(ai_models_dir))

from service.main import app
from service.model_loader import container


@pytest.fixture(scope="module", autouse=True)
def load_artifacts():
    """Ensures model artifacts are loaded before tests run."""
    container.load_artifacts()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


def test_model_loaded():
    """Verify that model container loaded model.joblib, schema.json, and metadata.json."""
    assert container.is_loaded is True
    assert container.model is not None
    assert container.schema is not None
    assert container.metadata is not None


def test_health(client):
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert "model_version" in data


def test_model_info(client):
    """Test GET /model-info endpoint."""
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "metrics" in data
    assert data["target"] == "fuel_consumption_comb"
    assert data["target_unit"] == "L/100 km"


def test_predict_valid(client):
    """Test POST /predict endpoint with valid features."""
    payload = {
        "features": {
            "model_year": 2022,
            "make": "TOYOTA",
            "vehicle_class": "COMPACT",
            "engine_size": 2.5,
            "cylinders": 4,
            "transmission": "AS6",
            "fuel_type": "X"
        }
    }
    headers = {"X-Request-ID": "test-req-12345"}
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["prediction"], float)
    assert data["prediction"] > 0
    assert data["unit"] == "L/100 km"
    assert data["request_id"] == "test-req-12345"


def test_predict_missing_field(client):
    """Test POST /predict with missing required feature."""
    payload = {
        "features": {
            "model_year": 2022,
            "make": "TOYOTA",
            # missing vehicle_class
            "engine_size": 2.5,
            "cylinders": 4,
            "transmission": "AS6",
            "fuel_type": "X"
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code in [400, 422]


def test_predict_invalid_type(client):
    """Test POST /predict with invalid data type for numeric feature."""
    payload = {
        "features": {
            "model_year": "invalid_year_str",
            "make": "TOYOTA",
            "vehicle_class": "COMPACT",
            "engine_size": 2.5,
            "cylinders": 4,
            "transmission": "AS6",
            "fuel_type": "X"
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code in [400, 422]


def test_predict_invalid_category(client):
    """Test POST /predict with invalid category value."""
    payload = {
        "features": {
            "model_year": 2022,
            "make": "UNKNOWN_MAKE_ABC",
            "vehicle_class": "COMPACT",
            "engine_size": 2.5,
            "cylinders": 4,
            "transmission": "AS6",
            "fuel_type": "X"
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "không hợp lệ" in data["detail"].lower() or "invalid" in data["detail"].lower()

import pytest
from api.app import create_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch("api.controllers.users_controller.service")
def test_create_user(mock_service, client):
    mock_service.create_user.return_value = "fakeid"
    resp = client.post("/api/users", json={"name":"Alice","email":"a@b.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "id" in data

@patch("api.controllers.users_controller.service")
def test_list_users(mock_service, client):
    mock_service.list_users.return_value = [{"name":"Alice"}]
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert resp.get_json() == [{"name":"Alice"}]

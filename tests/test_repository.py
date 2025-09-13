from api.repositories.user_repository import UserRepository

def test_create_and_read(mongo_mock):
    repo = UserRepository(mongo_uri="mongomock://localhost")
    user = {"name":"Test","value":10}
    inserted_id = repo.create(user)
    assert inserted_id is not None
    all_users = repo.read_all()
    assert isinstance(all_users, list)
    assert any(u["name"] == "Test" for u in all_users)

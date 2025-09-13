import pytest
from pymongo import MongoClient
from api.repositories.user_repository import UserRepository
import mongomock
import os
import sys

@pytest.fixture
def mongo_mock(monkeypatch):
    # patch MongoClient in repository to use mongomock
    import api.repositories.user_repository as repo_module
    from mongomock import MongoClient as MockClient
    monkeypatch.setattr(repo_module, "MongoClient", MockClient)
    return MockClient()

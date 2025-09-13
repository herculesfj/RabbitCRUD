from repositories.user_repository import UserRepository
from messaging.producer import Producer

class UserService:
    def __init__(self, repo: UserRepository = None, producer: Producer = None):
        self.repo = repo or UserRepository()
        self.producer = producer or Producer()

    def create_user(self, user: dict):
        inserted_id = self.repo.create(user)
        # add id to data for consumer traceability
        data = user.copy()
        data["id"] = inserted_id
        self.producer.publish("create", data)
        return inserted_id

    def list_users(self):
        return self.repo.read_all()

    def update_user_by_name(self, name: str, data: dict):
        modified = self.repo.update_by_name(name, data)
        self.producer.publish("update", {"name": name, "new_data": data})
        return modified

    def delete_user_by_name(self, name: str):
        deleted = self.repo.delete_by_name(name)
        self.producer.publish("delete", {"name": name})
        return deleted

    def clear_all_users(self):
        """Remove todos os usuários do banco"""
        deleted_count = self.repo.clear_all()
        self.producer.publish("clear_all", {"deleted_count": deleted_count})
        return deleted_count
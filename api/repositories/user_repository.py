from pymongo import MongoClient
from typing import Dict, Any, List, Optional
from bson.objectid import ObjectId
from config import MONGO_URI

class UserRepository:
    def __init__(self, mongo_uri: str = MONGO_URI, db_name: str = "crud_db"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["items"]

    def create(self, user: Dict[str, Any]) -> str:
        res = self.collection.insert_one(user)
        return str(res.inserted_id)

    def read_all(self) -> List[Dict[str, Any]]:
        docs = list(self.collection.find({}))
        # Converter ObjectId para string
        for doc in docs:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
        return docs

    def read_by_id(self, _id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({"_id": ObjectId(_id)})
        if not doc:
            return None
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        return doc

    def update_by_name(self, name: str, data: Dict[str, Any]) -> int:
        res = self.collection.update_one({"name": name}, {"$set": data})
        return res.modified_count

    def delete_by_name(self, name: str) -> int:
        res = self.collection.delete_one({"name": name})
        return res.deleted_count

    def clear_all(self) -> int:
        """Remove todos os documentos da coleção"""
        res = self.collection.delete_many({})
        return res.deleted_count

from pymongo import MongoClient
from config import MONGO_URI
from bson.objectid import ObjectId

class UserRepository:
    def __init__(self, mongo_uri=MONGO_URI, db_name="crud_db"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["items"]

    def insert(self, data):
        return self.collection.insert_one(data)

    def find_by_id(self, _id):
        return self.collection.find_one({"_id": ObjectId(_id)})

    def update_by_id(self, _id, data):
        return self.collection.update_one({"_id": ObjectId(_id)}, {"$set": data})

    def delete_by_id(self, _id):
        return self.collection.delete_one({"_id": ObjectId(_id)})

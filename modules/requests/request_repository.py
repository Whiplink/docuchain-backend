from database.mongodb import db
from bson import ObjectId


class RequestRepository:
    def __init__(self):
        self.collection = db["requests"]

    def create(self, data: dict):
        return self.collection.insert_one(data).inserted_id

    def find_by_id(self, request_id: str):
        return self.collection.find_one({"_id": ObjectId(request_id)})

    def find_all(self):
        return list(self.collection.find())
    
    def find_by_user_id(self, user_id: str):
        return list(self.collection.find({"requestor_id": ObjectId(user_id)}))
    
    def update_status(self, request_id: str, status: str):
        return self.collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": status}}
        )
from database.mongodb import db
from .accounts_schemas import AccountsCreateDTO
from bson import ObjectId

class AccountRepository:
    def __init__(self):
        self.collection = db["accounts"]

    def create(self, user_data: dict):
        dto = AccountsCreateDTO(**user_data)
        return self.collection.insert_one(dto.model_dump())

    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})
    
    def find_by_id(self, user_id: str):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def get_all(self):
        return list(self.collection.find({}))
    
    def update_role(self, account_id: str, role: str):
        return self.collection.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": {"role": role}}
        )
    def delete(self, account_id: str):
        return self.collection.delete_one(
            {"_id": ObjectId(account_id)}
        )
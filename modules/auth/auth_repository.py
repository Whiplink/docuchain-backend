# from database.mongodb import db

# class AuthRepository:

#   @staticmethod
#   def findByEmail(email):
#     result = db.accounts.find_one({"email":email})
#     print(result)
#     if result:
#         result["_id"] = str(result["_id"])

#     return result

from database.mongodb import db
from bson import ObjectId
from datetime import datetime

class AuthRepository:
  def __init__(self):
    self.collection = db["accounts"]

  def find_by_email(self, email: str):
    return self.collection.find_one({"email": email})
  
  def save_otp(self, user_id: str, otp: str, otp_expires_at: datetime):
    return self.collection.update_one(
      {"_id": ObjectId(user_id)},
      {"$set": {"otp": otp, "otp_expires_at": otp_expires_at}}
    )
  
  def clear_otp(self, user_id):
    self.collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "otp": "",
                "otp_expires_at": datetime(1970,1,1)
            }
        }
    )
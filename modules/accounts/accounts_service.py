from .accounts_repository import AccountRepository
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

class AccountService:
    def __init__(self):
        self.repo = AccountRepository()

    def create_user(self, data: dict):
        if self.repo.find_by_email(data["email"]):
            raise ValueError("Email already exists")
        
        hashed_pw = generate_password_hash(data.get("password"))

        user = {
            "email": data["email"],
            "password": hashed_pw,
            "role": data.get("role", "Requestor"),
            "otp": "",
            "otp_expires_at": datetime(1970,1,1),
        }

        return str(self.repo.create(user).inserted_id)
    
    def get_all_users(self):
        users = self.repo.get_all()

        # IMPORTANT: remove sensitive fields like password
        for u in users:
            u["_id"] = str(u["_id"])
            u.pop("password", None)
            u.pop("otp", None)
            u.pop("otp_expires_at", None)

        return users
    
    def update_role(self, account_id: str, role: str) -> bool:
        result = self.repo.update_role(account_id, role)
        return result.matched_count > 0
    
    def delete_user(self, account_id: str) -> bool:
        result = self.repo.delete(account_id)
        return result.deleted_count > 0
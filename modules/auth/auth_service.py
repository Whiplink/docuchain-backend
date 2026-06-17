# from flask_jwt_extended import ( create_access_token )
# from werkzeug.security import check_password_hash
# from .auth_repository import AuthRepository
# from core.enums import Role
# from ..accounts.accounts_service import AccountService
# import secrets
# from datetime import datetime, timedelta, timezone
# from .email_service import EmailService

# class AuthService:
#   def __init__(self):
#     self.repo = AuthRepository()
#     self.AccountService = AccountService()
#     self.EmailService = EmailService()

#   def login(self, data: dict):
#     user = self.repo.find_by_email(data["email"])
#     if not user:
#       raise ValueError("Account not found")
    
#     if user.get("role") == Role.requestor:
#       raise ValueError("User not allowed")
    
#     if not check_password_hash(user["password"], data["password"]):
#       raise ValueError("Invalid Password")
    
#     additional_claims = {"role": user.get("role")}
#     access_token = create_access_token(identity=str(user["_id"]), additional_claims=additional_claims)

#     return access_token
  
#   def send_otp(self, data: dict):
#     user = self.repo.find_by_email(data["email"])

#     if not user:
#       self.AccountService.create_user({
#         "email": data["email"],
#         "password": "requestor_password",
#         "role": Role.requestor
#       })

#       user = self.repo.find_by_email(data["email"])

    
#     if user.get("role") != Role.requestor:
#       raise ValueError("User not allowed")

#     OTP_EXPIRY_MINUTES = 5
#     otp = f"{secrets.randbelow(1000000):06d}"
#     otp_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()

#     self.repo.save_otp(user["_id"], otp, otp_expires_at)

#     self.EmailService.send_otp(
#        user["email"],
#        otp
#     )

#     return str(user["_id"])
  
#   def verify_otp(self, data: dict):
#     user = self.repo.find_by_email(data["email"])

#     if not user:
#         raise ValueError("User not found")

#     stored_otp = user.get("otp")
#     expires_at = user.get("otp_expires_at")

#     if not stored_otp or not expires_at:
#         raise ValueError("No active OTP found")

#     if stored_otp != data["otp"]:
#         raise ValueError("Invalid OTP")
    
#     if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at):
#         raise ValueError("OTP has expired")

#     # Prevent OTP reuse
#     self.repo.clear_otp(user["_id"])

#     additional_claims = {"role": user.get("role")}
#     access_token = create_access_token(identity=str(user["_id"]), additional_claims=additional_claims)

#     return access_token

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from .auth_repository import AuthRepository
from core.enums import Role
from ..accounts.accounts_service import AccountService
from .email_service import EmailService

import secrets
from datetime import datetime, timedelta, timezone
from threading import Thread


class AuthService:
    def __init__(self):
        self.repo = AuthRepository()
        self.account_service = AccountService()
        self.email_service = EmailService()

    # ---------------- LOGIN ----------------
    def login(self, data: dict):
        user = self.repo.find_by_email(data["email"])

        if not user:
            raise ValueError("Account not found")

        if user.get("role") == Role.requestor:
            raise ValueError("User not allowed")

        if not check_password_hash(user["password"], data["password"]):
            raise ValueError("Invalid Password")

        token = create_access_token(
            identity=str(user["_id"]),
            additional_claims={"role": user.get("role")}
        )

        return token

    # ---------------- SEND OTP ----------------
    def send_otp(self, data: dict):
        user = self.repo.find_by_email(data["email"])

        if not user:
            self.account_service.create_user({
                "email": data["email"],
                "password": "requestor_password",
                "role": Role.requestor
            })
            user = self.repo.find_by_email(data["email"])

        if user.get("role") != Role.requestor:
            raise ValueError("User not allowed")

        otp = f"{secrets.randbelow(1000000):06d}"

        expires_at = (
            datetime.now(timezone.utc) +
            timedelta(minutes=5)
        ).isoformat()

        self.repo.save_otp(user["_id"], otp, expires_at)

        # ✅ FIX: async email (NON-BLOCKING)
        Thread(
            target=self.email_service.send_otp,
            args=(user["email"], otp),
            daemon=True
        ).start()

        return str(user["_id"])

    # ---------------- VERIFY OTP ----------------
    def verify_otp(self, data: dict):
        user = self.repo.find_by_email(data["email"])

        if not user:
            raise ValueError("User not found")

        stored_otp = user.get("otp")
        expires_at = user.get("otp_expires_at")

        if not stored_otp or not expires_at:
            raise ValueError("No active OTP found")

        if stored_otp != data["otp"]:
            raise ValueError("Invalid OTP")

        if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at):
            raise ValueError("OTP has expired")

        # prevent reuse
        self.repo.clear_otp(user["_id"])

        token = create_access_token(
            identity=str(user["_id"]),
            additional_claims={"role": user.get("role")}
        )

        return token
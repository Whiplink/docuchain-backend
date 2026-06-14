from datetime import datetime
from .request_repository import RequestRepository
from ..accounts.accounts_repository import AccountRepository
from core.enums import Role


class RequestService:
    def __init__(self):
        self.repo = RequestRepository()
        self.AccountRepo = AccountRepository()

    def create_request(self, user_id: str, payload: dict):
        user = self.AccountRepo.find_by_id(user_id)

        if not user: 
            raise ValueError("No user found")

        data = {
            "requestor_id": user["_id"],
            "lrn": payload["lrn"],
            "name": payload["name"],
            "academic_year": payload["academic_year"],
            "purpose": payload["purpose"],

            # server-generated fields
            "status": "Pending",
            "comments": "",
            "date_requested": datetime.utcnow(),
        }

        return self.repo.create(data)

    def get_request(self, user_id: str, role: str, request_id: str):
        # return self.repo.find_by_id(request_id)

        request = self.repo.find_by_id(request_id)

        if role == Role.admin:
            return request
        
        if str(request["requestor_id"]) != user_id:
            raise ValueError("Forbidden: User is not the owner of the request")
        
        return request


    def get_all_requests(self, user_id: str , role: str):
        if role in (Role.admin, Role.registrar):
            return self.repo.find_all()
        return self.repo.find_by_user_id(user_id)
    
    def update_status(self, request_id: str, status: str) -> bool:
        result = self.repo.update_status(request_id, status)
        return result.matched_count > 0
        

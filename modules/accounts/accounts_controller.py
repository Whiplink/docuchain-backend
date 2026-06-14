from flask import Blueprint, request, jsonify
from .accounts_service import AccountService
from .accounts_schemas import AccountsRequestDTO, AccountsResponseDTO, AccountsRoleDTO
from core.auth.decorators import roles_required
from core.enums import Role

accounts_bp = Blueprint("accounts_bp", __name__, url_prefix="/api/accounts")
service = AccountService()

@accounts_bp.post("")
@roles_required(Role.admin)
def create_account():
  payload = AccountsRequestDTO(**request.json)
  user_id = service.create_user(payload.model_dump())

  return jsonify({
    "message": "User created",
    "id": user_id
  }), 201

@accounts_bp.get("")
@roles_required(Role.admin)
def get_all_accounts():
    users = service.get_all_users()
    for doc in users:
        doc["id"] = str(doc["_id"])
        del doc["_id"]

    return jsonify([
        AccountsResponseDTO(**doc).model_dump()
        for doc in users
    ])

@accounts_bp.patch("/<account_id>/role")
@roles_required(Role.admin)
def update_role(account_id):
    payload = AccountsRoleDTO(**request.json)

    success = service.update_role(
        account_id,
        payload.role
    )

    if not success:
        return jsonify({"message": "Account not found"}), 404

    return jsonify({"message": "Role updated successfully"})

@accounts_bp.delete("/<account_id>")
@roles_required(Role.admin)
def delete_account(account_id):
    success = service.delete_user(account_id)

    if not success:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200
   
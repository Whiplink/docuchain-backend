from flask import Blueprint, request, jsonify
from .request_service import RequestService
from .request_schemas import RequestCreate, RequestResponse, RequestStatusPatch
from core.auth.decorators import roles_required
from core.enums import Role
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

requests_bp = Blueprint("requests_bp", __name__, url_prefix="/api/requests")
service = RequestService()

@requests_bp.post("")
@jwt_required()
def create_request():
    user_id = get_jwt_identity()

    payload = RequestCreate(**request.json)

    inserted_id = service.create_request(user_id, payload.model_dump())

    return jsonify({
        "message": "Request created successfully",
        "id": str(inserted_id)
    }), 201


@requests_bp.get("")
@jwt_required()
def get_all_requests():
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    data = service.get_all_requests(user_id, role)

    for doc in data:
        doc["id"] = str(doc["_id"])
        doc["requestor_id"] = str(doc["requestor_id"])
        del doc["_id"]

    return jsonify([
        RequestResponse(**doc).model_dump()
        for doc in data
    ])


@requests_bp.get("/<request_id>")
@jwt_required()
def get_request(request_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()
    
    doc = service.get_request(user_id, role, request_id)

    if not doc:
        return jsonify({"message": "Not found"}), 404
    
    doc["id"] = str(doc["_id"])
    doc["requestor_id"] = str(doc["requestor_id"])
    del doc["_id"]

    return jsonify(RequestResponse(**doc).model_dump())

@requests_bp.patch("/<request_id>/status")
@roles_required(Role.admin, Role.registrar)
def update_status(request_id):
    payload = RequestStatusPatch(**request.json)

    success = service.update_status(
        request_id,
        payload.status
    )

    if not success:
        return jsonify({"message": "Request not found"}), 404

    return jsonify({"message": "Status updated successfully"})

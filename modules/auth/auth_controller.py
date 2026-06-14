from flask import Blueprint, request, jsonify
from .auth_schemas import AuthRequestorOtpDTO, AuthLoginDTO, AuthVerifyOtpDTO
from .auth_service import AuthService

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")
service = AuthService()

@auth_bp.post("/requestor-otp")
def requestor_otp():
  payload = AuthRequestorOtpDTO(**request.json)
  user_id = service.send_otp(payload.model_dump())

  return jsonify({
    "message": "Otp Sent Successfully",
    "id": user_id
  }), 201

@auth_bp.post("/verify-otp")
def verify_otp():
  payload = AuthVerifyOtpDTO(**request.json)
  token = service.verify_otp(payload.model_dump())

  return jsonify({
    "message": "Logged in Successfully",
    "token": token
  }), 201

@auth_bp.post('/login')
def login():
  payload = AuthLoginDTO(**request.json)
  token = service.login(payload.model_dump())

  return jsonify({
    "message": "Logged in Successfully",
    "token": token
  }), 201
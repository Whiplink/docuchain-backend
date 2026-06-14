from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, decode_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
)

# JWT config
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["docuchaindb"]
requests = db["requests"]
accounts = db["accounts"]

def generate_otp():
    return "123123"

def checkRole():

    try:
        # Get identity from JWT
        user_identity = get_jwt_identity()

        if not user_identity:
            return None

        # Find user in MongoDB
        user = accounts.find_one({"_id": ObjectId(user_identity)})

        if not user:
            return None

        # Return role field
        return user.get("role")

    except (PyMongoError, Exception) as e:
        print(f"checkRole error: {e}")
        return None

# @app.route("/send-otp", methods=["POST"])
# def send_otp():
#     return jsonify({"message": "OTP sent successfully"})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    # Fake OTP check (replace with real logic)
    if otp != "123123":
        return jsonify({"msg": "Invalid OTP"}), 400

    # Create JWT token
    access_token = create_access_token(identity=email)

    return jsonify({
        "token": access_token
    })

@app.route("/get-email")
@jwt_required()
def get_email():
    email = get_jwt_identity()
    return jsonify(email)

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        # Validate request body
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Find user in MongoDB
        user = accounts.find_one({"email": email})

        # Check if user exists
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Compare password
        # Assumes password is hashed in DB
        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Create JWT token
        additional_claims = {"role": user.get("role", "user")}  # default to 'user' if no role
        access_token = create_access_token(identity=str(user["_id"]), additional_claims=additional_claims)

        return jsonify({
            "message": "Login successful",
            "token": access_token,
        }), 200

    except PyMongoError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/requests", methods=["GET"])
@jwt_required()
def get_requests():
    email = get_jwt_identity()
    try:
        docs = list(requests.find({"email": email}))
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return jsonify(docs), 200

    except PyMongoError as e:
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

@app.route("/api/requests/all", methods=["GET"])
@jwt_required()
def get_all_requests():

    allowed_roles = ["admin", "registrar"]

    role = checkRole()

    if not role or role not in allowed_roles:
        return jsonify({"msg": "Unauthorized"}), 401

    try:
        docs = list(requests.find())
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return jsonify(docs), 200

    except PyMongoError as e:
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500
    

@app.route("/api/requests", methods=["POST"])
@jwt_required()
def submit_request():
    email = get_jwt_identity()
    lrn = request.json.get("lrn")
    name = request.json.get("name")
    academic_year = request.json.get("academic_year")
    purpose = request.json.get("purpose")
    status = "Pending"
    comments = ""
    date_requested = datetime.now(ZoneInfo("Asia/Manila"))

    try:
        result = requests.insert_one({
            "email": email,
            "lrn": lrn,
            "name": name,
            "academic_year": academic_year,
            "purpose": purpose,
            "status": status,
            "comments": comments,
            "date_requested": date_requested
        })
        return jsonify({"msg": "Request submitted successfully"}), 200
    except PyMongoError as e:
        return jsonify({"msg": "Failed to submit request", "error": str(e)}), 500
    
@app.route("/api/requests/<request_id>/status", methods=["POST"])
@jwt_required()
def update_request_status(request_id):

    allowed_roles = ["admin", "registrar"]

    role = checkRole()
    print(role)
    if not role or role not in allowed_roles:
        return jsonify({"msg": "Unauthorized"}), 401
    

    new_status = request.json.get("status")

    # Allowed values
    allowed_statuses = ["Pending", "Approved", "Denied"]

    if new_status not in allowed_statuses:
        return jsonify({"msg": "Invalid status value"}), 400

    try:
        # Find existing request
        existing_request = requests.find_one({"_id": ObjectId(request_id)})

        if not existing_request:
            return jsonify({"msg": "Request not found"}), 404

        # Check if same status
        if existing_request.get("status") == new_status:
            return jsonify({"msg": "Status is already set to this value"}), 200

        # Update status
        requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": new_status}}
        )

        return jsonify({"msg": "Status updated successfully"}), 200

    except PyMongoError as e:
        return jsonify({"msg": "Failed to update status", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"msg": "Invalid request ID", "error": str(e)}), 400
    



# Run server
if __name__ == "__main__":
    app.run()
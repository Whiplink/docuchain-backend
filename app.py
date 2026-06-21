import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
from datetime import timedelta
from flask_cors import CORS


from modules.requests.request_controller import requests_bp
from modules.accounts.accounts_controller import accounts_bp
from modules.auth.auth_controller import auth_bp

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS(app, origins=["http://localhost:3000"])
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=365)
jwt = JWTManager(app)

app.register_blueprint(requests_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(auth_bp)

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({
        "success": False,
        "error": e.name,
        "message": e.description
    }), e.code


@app.errorhandler(Exception)
def handle_unexpected_exception(e):
    app.logger.exception("Unhandled exception occurred")

    return jsonify({
        "success": False,
        "error": "Internal Server Error",
        # "message": "Something went wrong on the server"
        "message": str(e)
    }), 500

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        "success": False,
        "error": "ValidationError",
        "message": "Invalid request data",
        "details": [
            {"field": ".".join(map(str, err["loc"])), "message": err["msg"]}
            for err in e.errors()
        ]
    }), 422


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
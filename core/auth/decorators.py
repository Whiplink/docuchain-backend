from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            role = get_jwt().get("role")

            if role not in roles:
                return {"msg": "Forbidden: role not allowed"}, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
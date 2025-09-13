from flask import Blueprint, request, jsonify
from services.user_service import UserService
from models.user_model import User
from pydantic import ValidationError

bp = Blueprint("users", __name__, url_prefix="/api")

service = UserService()

@bp.route("/users", methods=["POST"])
def create_user():
    try:
        payload = request.get_json()
        user = User(**payload)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    inserted_id = service.create_user(user.dict(exclude_none=True))
    return jsonify({"status": "created", "id": inserted_id}), 201

@bp.route("/users", methods=["GET"])
def list_users():
    users = service.list_users()
    return jsonify(users), 200

@bp.route("/users/<string:name>", methods=["PUT"])
def update_user(name):
    data = request.get_json()
    modified = service.update_user_by_name(name, data)
    return jsonify({"modified": modified}), 200

@bp.route("/users/<string:name>", methods=["DELETE"])
def delete_user(name):
    deleted = service.delete_user_by_name(name)
    return jsonify({"deleted": deleted}), 200

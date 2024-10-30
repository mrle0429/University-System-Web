from flask import Blueprint, jsonify
from ..models import User

user_api = Blueprint('user_api', __name__)

@user_api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list)

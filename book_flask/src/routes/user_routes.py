from flask import Blueprint

from services import user_service

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
@user_bp.route('/users/<name>', methods=['GET'])
def list_users(name=None):
    return user_service.get_user_by_name(name=name)
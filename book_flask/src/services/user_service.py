from flask import Response, jsonify
from logger import logger
from services.db import db
from models.user import User

# TODO remove
def get_user_by_name(name: str):
    users = []
    if name:
        users.append(User.query.filter_by(name=name).first())
        logger.info(f'User found: {users[0]}')
    else:
        users.extend(User.query.all())
    logger.info(f'Users found: {len(users)}')
    return jsonify([{"id": u.id, "name": u.username} for u in users])
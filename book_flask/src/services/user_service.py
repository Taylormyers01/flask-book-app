from flask import Response, jsonify
from logger import logger
from services.db import db
from models.user import user


def get_user_by_name(name: str):
    users = []
    if name:
        users.append(user.query.filter_by(name=name).first())
        logger.info(f'User found: {users[0]}')
    else:
        users.extend(user.query.all())
    logger.info(f'Users found: {len(users)}')
    return jsonify([{"id": u.id, "name": u.name} for u in users])

def add_user(name):
    logger.info(f'adding user {name}')
    new_user = user(name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added", "user": {"id": new_user.id, "name": new_user.name}})
    
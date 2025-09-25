from models.user import User
from services.db import db
from logger import logger
import json

def register_user(username, password):
    reg_user = User(username=username)
    logger.info(f"Registering user: {username}")
    reg_user.set_password(password)
    db.session.add(reg_user)
    db.session.commit()
    return reg_user

def authenticate_user(username, password):
    auth_user = User.query.filter_by(username=username).first()
    if auth_user and auth_user.check_password(password):
        return auth_user
    return None

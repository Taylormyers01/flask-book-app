from sqlalchemy import  Column
from sqlalchemy.orm import relationship
from services.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__='users'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(80), unique=True, nullable=False)
    password_hash = Column(db.String(128), nullable=False)
    user_books = db.relationship("UserBook", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_book(self, g_id):
        return next((ub.book for ub in self.user_books if ub.book.g_id == g_id), None)
    
    def get_book_by_position(self, position):
        return next((ub for ub in self.user_books if ub.shelf_pos == position), None)
    
    def get_user_book(self, g_id):
        return next((ub for ub in self.user_books if ub.book.g_id == g_id), None)

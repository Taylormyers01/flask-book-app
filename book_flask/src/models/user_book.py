from sqlalchemy import Enum

from models.constants import BookStatus
from services.db import db


class UserBook(db.Model):
    __tablename__='book_users'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    status = db.Column(Enum(BookStatus), default=BookStatus.NONE)
    shelf_pos = db.Column(db.Integer)
    owned = db.Column(db.Boolean)

    user = db.relationship("User", back_populates="user_books")
    book = db.relationship("Book", back_populates="user_books")



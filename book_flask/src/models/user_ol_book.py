from sqlalchemy import Enum

from models.constants import BookStatus
from services.db import db


class UserOlBook(db.Model):
    __tablename__='user_ol_books'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    ol_book_id = db.Column(db.Integer, db.ForeignKey('ol_books.id'), primary_key=True)

    status = db.Column(Enum(BookStatus), default=BookStatus.NONE)
    shelf_pos = db.Column(db.Integer)
    owned = db.Column(db.Boolean)

    user = db.relationship("User", back_populates="user_ol_books")
    ol_book = db.relationship("OlBook", back_populates="user_ol_books")
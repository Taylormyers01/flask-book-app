from sqlalchemy import  Column
from services.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__='users'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(80), unique=True, nullable=False)
    password_hash = Column(db.String(128), nullable=False)
    user_ol_books = db.relationship("UserOlBook", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_ol_book(self, ol_id):
        """
        Get book by ol_id

        :param ol_id: OpenLibrary identifier
        :return: OlBook
        """
        return next((uolb.ol_book for uolb in self.user_ol_books if uolb.book.ol_id == ol_id), None)

    def get_ol_book_by_position(self, position):
        """
        Get book by position on the shelf

        :param position: shelf position
        :return: OlBook
        """
        return next((uolb for uolb in self.user_ol_books if uolb.shelf_pos == position), None)

    def get_user_ol_book(self, ol_id):
        """
        Get UserOlBook relationship object

        :param ol_id: OpenLibrary identifier
        :return: UserOlBook
        """
        return next((uolb for uolb in self.user_ol_books if uolb.ol_book.ol_id == ol_id), None)
